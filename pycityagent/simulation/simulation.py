import asyncio
import inspect
import json
import logging
import time
import uuid
from collections.abc import Callable
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Literal, Optional, Type, Union, cast

import ray
import yaml
from langchain_core.embeddings import Embeddings

from ..agent import Agent, InstitutionAgent
from ..cityagent import (BankAgent, FirmAgent, GovernmentAgent, NBSAgent,
                         SocietyAgent)
from ..cityagent.initial import bind_agent_info, initialize_social_network
from ..cityagent.memory_config import (memory_config_bank, memory_config_firm,
                                       memory_config_government,
                                       memory_config_init, memory_config_nbs,
                                       memory_config_societyagent)
from ..cityagent.message_intercept import (EdgeMessageBlock,
                                           MessageBlockListener,
                                           PointMessageBlock)
from ..configs import ExpConfig, SimConfig
from ..environment import EconomyClient, Simulator
from ..llm import SimpleEmbedding
from ..message import (MessageBlockBase, MessageBlockListenerBase,
                       MessageInterceptor, Messager)
from ..metrics import init_mlflow_connection
from ..metrics.mlflow_client import MlflowClient
from ..survey import Survey
from ..utils import (SURVEY_SENDER_UUID, TO_UPDATE_EXP_INFO_KEYS_AND_TYPES,
                     WorkflowType)
from .agentgroup import AgentGroup
from .storage.pg import PgWriter, create_pg_tables

logger = logging.getLogger("pycityagent")
ExpConfig.model_rebuild()  # rebuild the schema due to circular import


__all__ = ["AgentSimulation"]


class AgentSimulation:
    """
    A class to simulate a multi-agent system.

    This simulation framework is designed to facilitate the creation and management of multiple agent types within an experiment.
    It allows for the configuration of different agents, memory configurations, and metric extractors, as well as enabling institutional settings.

    Attributes:
        exp_id (str): A unique identifier for the current experiment.
        agent_class (List[Type[Agent]]): A list of agent classes that will be instantiated in the simulation.
        agent_config_file (Optional[dict]): Configuration file or dictionary for initializing agents.
        logging_level (int): The level of logging to be used throughout the simulation.
        default_memory_config_func (Dict[Type[Agent], Callable]): Dictionary mapping agent classes to their respective memory configuration functions.
    """

    def __init__(
        self,
        config: SimConfig,
        agent_class: Union[None, type[Agent], list[type[Agent]]] = None,
        agent_class_configs: Optional[dict] = None,
        metric_extractors: Optional[list[tuple[int, Callable]]] = None,
        enable_institution: bool = True,
        agent_prefix: str = "agent_",
        exp_name: str = "default_experiment",
        logging_level: int = logging.WARNING,
    ):
        """
        Initializes the AgentSimulation with the given parameters.

        - **Description**:
            - Sets up the simulation environment based on the provided configuration. Depending on the `enable_institution` flag,
              it can include a predefined set of institutional agents. If specific agent classes are provided, those will be used instead.

        - **Args**:
            - `config` (SimConfig): The main configuration for the simulation.
            - `agent_class` (Union[None, Type[Agent], List[Type[Agent]]], optional):
                Either a single agent class or a list of agent classes to instantiate. Defaults to None, which implies a default set of agents.
            - `agent_class_configs` (Optional[dict], optional): An optional configuration dict used to initialize agents. Defaults to None.
            - `metric_extractors` (Optional[List[Tuple[int, Callable]]], optional):
                A list of tuples containing intervals and callables for extracting metrics from the simulation. Defaults to None.
            - `enable_institution` (bool, optional): Flag indicating whether institutional agents should be included in the simulation. Defaults to True.
            - `agent_prefix` (str, optional): Prefix string for naming agents. Defaults to "agent_".
            - `exp_name` (str, optional): The name of the experiment. Defaults to "default_experiment".
            - `logging_level` (int, optional): Logging level to set for the simulation's logger. Defaults to logging.WARNING.

        - **Returns**:
            - None
        """
        self.exp_id = str(uuid.uuid4())
        if isinstance(agent_class, list):
            self.agent_class = agent_class
        elif agent_class is None:
            if enable_institution:
                self.agent_class = [
                    SocietyAgent,
                    FirmAgent,
                    BankAgent,
                    NBSAgent,
                    GovernmentAgent,
                ]
                self.default_memory_config_func = {
                    SocietyAgent: memory_config_societyagent,
                    FirmAgent: memory_config_firm,
                    BankAgent: memory_config_bank,
                    NBSAgent: memory_config_nbs,
                    GovernmentAgent: memory_config_government,
                }
            else:
                self.agent_class = [SocietyAgent]
                self.default_memory_config_func = {
                    SocietyAgent: memory_config_societyagent
                }
        else:
            self.agent_class = [agent_class]
        self.agent_class_configs = agent_class_configs
        self.logging_level = logging_level
        self.config = config
        self.exp_name = exp_name
        simulator = Simulator(config, create_map=True)
        self._simulator = simulator
        self._map_ref = self._simulator.map
        server_addr = self._simulator.get_server_addr()
        config.SetServerAddress(server_addr)
        self._economy_client = EconomyClient(server_addr)
        if enable_institution:
            self._economy_addr = economy_addr = server_addr
        self.agent_prefix = agent_prefix
        self._groups: dict[str, AgentGroup] = {}  # type:ignore
        self._agent_uuid2group: dict[str, AgentGroup] = {}  # type:ignore
        self._agent_uuids: list[str] = []
        self._type2group: dict[Type[Agent], AgentGroup] = {}
        self._user_chat_topics: dict[str, str] = {}
        self._user_survey_topics: dict[str, str] = {}
        self._user_interview_topics: dict[str, str] = {}
        self._loop = asyncio.get_event_loop()
        self._total_steps = 0
        self._simulator_day = 0
        # self._last_asyncio_pg_task = None  # hide SQL write IO to calculation task

        mqtt_config = config.prop_mqtt
        self._messager = Messager.remote(
            hostname=mqtt_config.server,  # type:ignore
            port=mqtt_config.port,
            username=mqtt_config.username,
            password=mqtt_config.password,
        )

        # storage

        # avro
        avro_config = config.prop_avro_config
        if avro_config is not None:
            self._enable_avro: bool = avro_config.enabled  # type:ignore
            if not self._enable_avro:
                self._avro_path = None
                logger.warning("AVRO is not enabled, NO AVRO LOCAL STORAGE")
            else:
                self._avro_path = Path(avro_config.path) / f"{self.exp_id}"
                self._avro_path.mkdir(parents=True, exist_ok=True)
        else:
            self._avro_path = None
            logger.warning("AVRO is not enabled, NO AVRO LOCAL STORAGE")
            self._enable_avro = False

        # mlflow
        metric_config = config.prop_metric_request
        if metric_config is not None and metric_config.mlflow is not None:
            logger.info(f"-----Creating Mlflow client...")
            mlflow_run_id, _ = init_mlflow_connection(
                config=metric_config.mlflow,
                experiment_uuid=self.exp_id,
                mlflow_run_name=f"EXP_{self.exp_name}_{1000*int(time.time())}",
                experiment_name=self.exp_name,
            )
            self.mlflow_client = MlflowClient(
                config=metric_config.mlflow,
                experiment_uuid=self.exp_id,
                mlflow_run_name=f"EXP_{exp_name}_{1000*int(time.time())}",
                experiment_name=exp_name,
                run_id=mlflow_run_id,
            )
            self.metric_extractors = metric_extractors
        else:
            logger.warning("Mlflow is not enabled, NO MLFLOW STORAGE")
            self.mlflow_client = None
            self.metric_extractors = None

        # pg
        pgsql_config = config.prop_postgre_sql_config
        if pgsql_config is not None:
            self._enable_pgsql: bool = pgsql_config.enabled  # type:ignore
            if not self._enable_pgsql:
                logger.warning(
                    "PostgreSQL is not enabled, NO POSTGRESQL DATABASE STORAGE"
                )
                self._pgsql_dsn = ""
            else:
                self._pgsql_dsn = pgsql_config.dsn
        else:
            self._enable_pgsql = False

        # add experiment info related properties
        self._exp_created_time = datetime.now(timezone.utc)
        self._exp_updated_time = datetime.now(timezone.utc)
        self._exp_info = {
            "id": self.exp_id,
            "name": exp_name,
            "num_day": 0,  # will be updated in run method
            "status": 0,
            "cur_day": 0,
            "cur_t": 0.0,
            "config": str(config.model_dump()),
            "error": "",
            "created_at": self._exp_created_time.isoformat(),
            "updated_at": self._exp_updated_time.isoformat(),
        }

        # create async task to save experiment info
        if self._enable_avro:
            assert self._avro_path is not None
            self._exp_info_file = self._avro_path / "experiment_info.yaml"
            with open(self._exp_info_file, "w") as f:
                yaml.dump(self._exp_info, f)

    @classmethod
    async def run_from_config(cls, config: ExpConfig, sim_config: SimConfig):
        """Directly run from config file
        Basic config file should contain:
        - simulation_config: file_path
        - enable_institution: Optional[bool], default is True
        - llm_semaphore: Optional[int], default is 200
        - agent_config:
            - agent_config_file: Optional[dict[type[Agent], str]]
            - memory_config_init_func: Optional[Callable]
            - memory_config_func: Optional[dict[type[Agent], Callable]]
            - metric_extractors: Optional[list[tuple[int, Callable]]]
            - init_func: Optional[list[Callable[AgentSimulation, None]]]
            - group_size: Optional[int]
            - embedding_model: Optional[EmbeddingModel]
            - number_of_citizen: required, int
            - number_of_firm: required, int
            - number_of_government: required, int
            - number_of_bank: required, int
            - number_of_nbs: required, int
        - environment: Optional[dict[str, str]]
            - default: {'weather': 'The weather is normal', 'crime': 'The crime rate is low', 'pollution': 'The pollution level is low', 'temperature': 'The temperature is normal', 'day': 'Workday'}
        - workflow:
            - list[Step]
            - Step:
                - type: str, "step", "run", "interview", "survey", "intervene", "pause", "resume", "function"
                - days: int if type is "run", else None
                - times: int if type is "step", else None
                - description: Optional[str], description of the step
                - func: Optional[Callable[AgentSimulation, None]], only used when type is "interview", "survey", "intervene", "function"
        - message_intercept
            - mode: "point"|"edge"
            - max_violation_time: Optional[int], default to 3. The maximum time for someone to send bad message before banned. Used only in `point` mode.
        - logging_level: Optional[int]
        - exp_name: Optional[str]
        """

        agent_config = config.prop_agent_config

        logger.info("Creating AgentSimulation Task...")
        simulation = cls(
            config=sim_config,
            agent_class_configs=agent_config.agent_class_configs,
            metric_extractors=config.prop_metric_extractors,
            enable_institution=agent_config.enable_institution,
            exp_name=config.exp_name,
            logging_level=config.logging_level,
        )
        environment = config.prop_environment.model_dump()
        simulation._simulator.set_environment(environment)
        logger.info("Initializing Agents...")
        agent_count: dict[type[Agent], int] = {
            SocietyAgent: agent_config.number_of_citizen,
            FirmAgent: agent_config.number_of_firm,
            GovernmentAgent: agent_config.number_of_government,
            BankAgent: agent_config.number_of_bank,
            NBSAgent: agent_config.number_of_nbs,
        }
        if agent_count.get(SocietyAgent, 0) == 0:
            raise ValueError("number_of_citizen is required")

        # support MessageInterceptor
        if config.message_intercept is not None:
            intercept_config = config.message_intercept
            if intercept_config.mode == "point":
                _interceptor_blocks = [
                    PointMessageBlock(
                        max_violation_time=intercept_config.max_violation_time
                    )
                ]
            elif intercept_config.mode == "edge":
                _interceptor_blocks = [
                    EdgeMessageBlock(
                        max_violation_time=intercept_config.max_violation_time
                    )
                ]
            else:
                raise ValueError(
                    f"Unsupported interception mode `{intercept_config.mode}!`"
                )
            _message_intercept_kwargs = {
                "message_interceptor_blocks": _interceptor_blocks,
                "message_listener": MessageBlockListener(),
            }
        else:
            _message_intercept_kwargs = {}
        embedding_model = agent_config.embedding_model
        if embedding_model is None:
            embedding_model = SimpleEmbedding()
        await simulation.init_agents(
            agent_count=agent_count,
            group_size=agent_config.group_size,
            embedding_model=embedding_model,
            memory_config_func=agent_config.memory_config_func,
            memory_config_init_func=agent_config.memory_config_init_func,
            **_message_intercept_kwargs,
            environment=environment,
            llm_semaphore=config.llm_semaphore,
        )
        logger.info("Running Init Functions...")
        init_funcs = agent_config.init_func
        if init_funcs is None:
            init_funcs = [bind_agent_info, initialize_social_network]
        for init_func in init_funcs:
            if inspect.iscoroutinefunction(init_func):
                await init_func(simulation)
            else:
                init_func = cast(Callable, init_func)
                init_func(simulation)
        logger.info("Starting Simulation...")
        llm_log_lists = []
        mqtt_log_lists = []
        simulator_log_lists = []
        agent_time_log_lists = []
        for step in config.prop_workflow:
            logger.info(
                f"Running step: type: {step.type} - description: {step.description}"
            )
            if step.type not in {t.value for t in WorkflowType}:
                raise ValueError(f"Invalid step type: {step.type}")
            if step.type == WorkflowType.RUN:
                _days = cast(int, step.days)
                llm_log_list, mqtt_log_list, simulator_log_list, agent_time_log_list = (
                    await simulation.run(_days)
                )
                llm_log_lists.extend(llm_log_list)
                mqtt_log_lists.extend(mqtt_log_list)
                simulator_log_lists.extend(simulator_log_list)
                agent_time_log_lists.extend(agent_time_log_list)
            elif step.type == WorkflowType.STEP:
                times = cast(int, step.times)
                for _ in range(times):
                    (
                        llm_log_list,
                        mqtt_log_list,
                        simulator_log_list,
                        agent_time_log_list,
                    ) = await simulation.step()
                    llm_log_lists.extend(llm_log_list)
                    mqtt_log_lists.extend(mqtt_log_list)
                    simulator_log_lists.extend(simulator_log_list)
                    agent_time_log_lists.extend(agent_time_log_list)
            elif step.type == WorkflowType.PAUSE:
                await simulation.pause_simulator()
            elif step.type == WorkflowType.RESUME:
                await simulation.resume_simulator()
            elif step.type == WorkflowType.FUNCTION:
                _func = cast(Callable, step.func)
                await _func(simulation)
        logger.info("Simulation finished")
        return llm_log_lists, mqtt_log_lists, simulator_log_lists, agent_time_log_lists

    @property
    def enable_avro(
        self,
    ) -> bool:
        return self._enable_avro

    @property
    def enable_pgsql(
        self,
    ) -> bool:
        return self._enable_pgsql

    @property
    def avro_path(
        self,
    ) -> Path:
        return self._avro_path  # type:ignore

    @property
    def economy_client(self):
        return self._economy_client

    @property
    def groups(self):
        return self._groups

    @property
    def agent_uuids(self):
        return self._agent_uuids

    @property
    def agent_uuid2group(self):
        return self._agent_uuid2group

    @property
    def messager(self) -> ray.ObjectRef:
        return self._messager

    @property
    def message_interceptor(self) -> ray.ObjectRef:
        return self._message_interceptors[0]  # type:ignore

    async def _save_exp_info(self) -> None:
        """Async save experiment info to YAML file"""
        try:
            if self.enable_avro:
                with open(self._exp_info_file, "w") as f:
                    yaml.dump(self._exp_info, f)
        except Exception as e:
            logger.error(f"Avro save experiment info failed: {str(e)}")
        try:
            if self.enable_pgsql:
                worker: ray.ObjectRef = self._pgsql_writers[0]  # type:ignore
                pg_exp_info = {
                    k: self._exp_info[k] for (k, _) in TO_UPDATE_EXP_INFO_KEYS_AND_TYPES
                }
                pg_exp_info["created_at"] = self._exp_created_time
                pg_exp_info["updated_at"] = self._exp_updated_time
                await worker.async_update_exp_info.remote(  # type:ignore
                    pg_exp_info
                )
        except Exception as e:
            logger.error(f"PostgreSQL save experiment info failed: {str(e)}")

    async def _update_exp_status(self, status: int, error: str = "") -> None:
        self._exp_updated_time = datetime.now(timezone.utc)
        """Update experiment status and save"""
        self._exp_info["status"] = status
        self._exp_info["error"] = error
        self._exp_info["updated_at"] = self._exp_updated_time.isoformat()
        await self._save_exp_info()

    async def _monitor_exp_status(self, stop_event: asyncio.Event):
        """Monitor experiment status and update

        - **Args**:
            stop_event: event for notifying monitor task to stop
        """
        try:
            while not stop_event.is_set():
                # update experiment status
                # assume all groups' cur_day and cur_t are synchronized, take the first one
                self._exp_info["cur_day"] = await self._simulator.get_simulator_day()
                self._exp_info["cur_t"] = (
                    await self._simulator.get_simulator_second_from_start_of_day()
                )
                await self._save_exp_info()

                await asyncio.sleep(1)  # avoid too frequent updates
        except asyncio.CancelledError:
            # normal cancellation, no special handling needed
            pass
        except Exception as e:
            logger.error(f"Error monitoring experiment status: {str(e)}")
            raise

    async def __aenter__(self):
        """Async context manager entry"""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if exc_type is not None:
            # if exception occurs, update status to error
            await self._update_exp_status(3, str(exc_val))
        elif self._exp_info["status"] != 3:
            # if no exception and status is not error, update to finished
            await self._update_exp_status(2)

    async def pause_simulator(self):
        await self._simulator.pause()

    async def resume_simulator(self):
        await self._simulator.resume()

    async def init_agents(
        self,
        agent_count: dict[type[Agent], int],
        group_size: int = 10000,
        pg_sql_writers: int = 32,
        message_interceptors: int = 1,
        message_interceptor_blocks: Optional[list[MessageBlockBase]] = None,
        social_black_list: Optional[list[tuple[str, str]]] = None,
        message_listener: Optional[MessageBlockListenerBase] = None,
        embedding_model: Embeddings = SimpleEmbedding(),
        memory_config_init_func: Optional[Callable] = None,
        memory_config_func: Optional[dict[type[Agent], Callable]] = None,
        environment: dict[str, str] = {},
        llm_semaphore: int = 200,
    ) -> None:
        """
        Initialize agents within the simulation.

        - **Description**:
            - Asynchronously initializes a specified number of agents for each provided agent class.
            - Agents are grouped into independent Ray actors based on the `group_size`, with configurations for database writers,
              message interceptors, and memory settings. Optionally updates the simulator's environment variables.

        - **Args**:
            - `agent_count` (dict[Type[Agent], int]): Dictionary mapping agent classes to the number of instances to create.
            - `group_size` (int, optional): Number of agents per group, each group runs as an independent Ray actor. Defaults to 10000.
            - `pg_sql_writers` (int, optional): Number of independent PgSQL writer processes. Defaults to 32.
            - `message_interceptors` (int, optional): Number of message interceptor processes. Defaults to 1.
            - `message_interceptor_blocks` (Optional[List[MessageBlockBase]], optional): List of message interception blocks. Defaults to None.
            - `social_black_list` (Optional[List[Tuple[str, str]]], optional): List of tuples representing pairs of agents that should not communicate. Defaults to None.
            - `message_listener` (Optional[MessageBlockListenerBase], optional): Listener for intercepted messages. Defaults to None.
            - `embedding_model` (Embeddings, optional): Model used for generating embeddings for agents' memories. Defaults to SimpleEmbedding().
            - `memory_config_init_func` (Optional[Callable], optional): Initialization function for setting up memory configuration. Defaults to None.
            - `memory_config_func` (Optional[Dict[Type[Agent], Callable]], optional): Dictionary mapping agent classes to their memory configuration functions. Defaults to None.
            - `environment` (Optional[Dict[str, str]], optional): Environment variables to update in the simulation. Defaults to None.

        - **Raises**:
            - `ValueError`: If the lengths of `agent_class` and `agent_count` do not match.

        - **Returns**:
            - `None`
        """
        self.agent_count = agent_count
        if len(self.agent_class) != len(agent_count):
            raise ValueError("The length of agent_class and agent_count does not match")

        if memory_config_init_func is not None:
            await memory_config_init(self)
        if memory_config_func is None:
            memory_config_func = self.default_memory_config_func  # type:ignore

        # use thread pool to create AgentGroup
        group_creation_params = []

        # process institution agent and citizen agent
        institution_params = []
        citizen_params = []

        # collect all parameters
        for i in range(len(self.agent_class)):
            agent_class = self.agent_class[i]
            agent_count_i = agent_count[agent_class]
            assert memory_config_func is not None
            memory_config_func_i = memory_config_func.get(
                agent_class, self.default_memory_config_func[agent_class]  # type:ignore
            )

            if self.agent_class_configs is not None:
                config_file = self.agent_class_configs.get(agent_class, None)
            else:
                config_file = None

            if issubclass(agent_class, InstitutionAgent):
                institution_params.append(
                    (agent_class, agent_count_i, memory_config_func_i, config_file)
                )
            else:
                citizen_params.append(
                    (agent_class, agent_count_i, memory_config_func_i, config_file)
                )

        # process institution group
        if institution_params:
            total_institution_count = sum(p[1] for p in institution_params)
            num_institution_groups = (
                total_institution_count + group_size - 1
            ) // group_size

            for k in range(num_institution_groups):
                start_idx = k * group_size
                remaining = total_institution_count - start_idx
                number_of_agents = min(remaining, group_size)

                agent_classes = []
                agent_counts = []
                memory_config_funcs = {}
                config_files = {}

                # assign each type of institution agent to current group
                curr_start = start_idx
                for agent_class, count, mem_func, conf_file in institution_params:
                    if curr_start < count:
                        agent_classes.append(agent_class)
                        agent_counts.append(min(count - curr_start, number_of_agents))
                        memory_config_funcs[agent_class] = mem_func
                        config_files[agent_class] = conf_file
                    curr_start = max(0, curr_start - count)

                group_creation_params.append(
                    (
                        agent_classes,
                        agent_counts,
                        memory_config_funcs,
                        f"InstitutionGroup_{k}",
                        config_files,
                    )
                )

        # process citizen group
        if citizen_params:
            total_citizen_count = sum(p[1] for p in citizen_params)
            num_citizen_groups = (total_citizen_count + group_size - 1) // group_size

            for k in range(num_citizen_groups):
                start_idx = k * group_size
                remaining = total_citizen_count - start_idx
                number_of_agents = min(remaining, group_size)

                agent_classes = []
                agent_counts = []
                memory_config_funcs = {}
                config_files = {}

                # assign each type of citizen agent to current group
                curr_start = start_idx
                for agent_class, count, mem_func, conf_file in citizen_params:
                    if curr_start < count:
                        agent_classes.append(agent_class)
                        agent_counts.append(min(count - curr_start, number_of_agents))
                        memory_config_funcs[agent_class] = mem_func
                        config_files[agent_class] = conf_file
                    curr_start = max(0, curr_start - count)

                group_creation_params.append(
                    (
                        agent_classes,
                        agent_counts,
                        memory_config_funcs,
                        f"CitizenGroup_{k}",
                        config_files,
                    )
                )
        # initialize mlflow connection
        metric_config = self.config.prop_metric_request
        if metric_config is not None and metric_config.mlflow is not None:
            mlflow_run_id, _ = init_mlflow_connection(
                experiment_uuid=self.exp_id,
                config=metric_config.mlflow,
                mlflow_run_name=f"{self.exp_name}_{1000*int(time.time())}",
                experiment_name=self.exp_name,
            )
        else:
            mlflow_run_id = None
        # create table
        if self.enable_pgsql:
            _num_workers = min(1, pg_sql_writers)
            create_pg_tables(
                exp_id=self.exp_id,
                dsn=self._pgsql_dsn,
            )
            self._pgsql_writers = _workers = [
                PgWriter.remote(self.exp_id, self._pgsql_dsn)
                for _ in range(_num_workers)
            ]
        else:
            _num_workers = 1
            self._pgsql_writers = _workers = [None for _ in range(_num_workers)]
        # message interceptor
        self.message_listener = message_listener
        if message_listener is not None:
            self._message_abort_listening_queue = _queue = ray.util.queue.Queue()  # type: ignore
            await message_listener.set_queue(_queue)
        else:
            self._message_abort_listening_queue = _queue = None
        _interceptor_blocks = message_interceptor_blocks
        _black_list = [] if social_black_list is None else social_black_list
        _llm_config = self.config.llm_request
        if message_interceptor_blocks is not None:
            _num_interceptors = min(1, message_interceptors)
            self._message_interceptors = _interceptors = [
                MessageInterceptor.remote(
                    _interceptor_blocks,  # type:ignore
                    _black_list,
                    _llm_config,
                    _queue,
                )
                for _ in range(_num_interceptors)
            ]
        else:
            _num_interceptors = 1
            self._message_interceptors = _interceptors = [
                None for _ in range(_num_interceptors)
            ]
        creation_tasks = []
        for i, (
            agent_class,
            number_of_agents,
            memory_config_function_group,
            group_name,
            config_file,
        ) in enumerate(group_creation_params):
            # create async task directly
            group = AgentGroup.remote(
                agent_class,
                number_of_agents,
                memory_config_function_group,
                self.config,
                self._map_ref,
                self.exp_name,
                self.exp_id,
                self.enable_avro,
                self.avro_path,
                self.enable_pgsql,
                _workers[i % _num_workers],  # type:ignore
                self.message_interceptor,
                mlflow_run_id,
                embedding_model,
                self.logging_level,
                config_file,
                llm_semaphore,
                environment,
            )
            creation_tasks.append((group_name, group))

        # update data structure
        for group_name, group in creation_tasks:
            self._groups[group_name] = group
            group_agent_uuids = ray.get(group.get_agent_uuids.remote())
            for agent_uuid in group_agent_uuids:
                self._agent_uuids.append(agent_uuid)
                self._agent_uuid2group[agent_uuid] = group
                self._user_chat_topics[agent_uuid] = (
                    f"exps/{self.exp_id}/agents/{agent_uuid}/user-chat"
                )
                self._user_survey_topics[agent_uuid] = (
                    f"exps/{self.exp_id}/agents/{agent_uuid}/user-survey"
                )
            group_agent_type = ray.get(group.get_agent_type.remote())
            for agent_type in group_agent_type:
                if agent_type not in self._type2group:
                    self._type2group[agent_type] = []
                self._type2group[agent_type].append(group)

        # parallel initialize all groups' agents
        await self.resume_simulator()
        init_tasks = []
        for group in self._groups.values():
            init_tasks.append(group.init_agents.remote())
        ray.get(init_tasks)
        await self.messager.connect.remote()  # type:ignore
        await self.messager.subscribe.remote(  # type:ignore
            [(f"exps/{self.exp_id}/user_payback", 1)], [self.exp_id]
        )
        await self.messager.start_listening.remote()  # type:ignore

        agent_ids = set()
        org_ids = set()
        for group in self._groups.values():
            ids = await group.get_economy_ids.remote()
            agent_ids.update(ids[0])
            org_ids.update(ids[1])
        await self.economy_client.set_ids(agent_ids, org_ids)
        for group in self._groups.values():
            await group.set_economy_ids.remote(agent_ids, org_ids)

    async def gather(
        self, content: str, target_agent_uuids: Optional[list[str]] = None
    ):
        """
        Collect specific information from agents.

        - **Description**:
            - Asynchronously gathers specified content from targeted agents within all groups.

        - **Args**:
            - `content` (str): The information to collect from the agents.
            - `target_agent_uuids` (Optional[List[str]], optional): A list of agent UUIDs to target. Defaults to None, meaning all agents are targeted.

        - **Returns**:
            - Result of the gathering process as returned by each group's `gather` method.
        """
        gather_tasks = []
        for group in self._groups.values():
            gather_tasks.append(group.gather.remote(content, target_agent_uuids))
        return await asyncio.gather(*gather_tasks)

    async def filter(
        self,
        types: Optional[list[Type[Agent]]] = None,
        keys: Optional[list[str]] = None,
        values: Optional[list[Any]] = None,
    ) -> list[str]:
        """
        Filter out agents of specified types or with matching key-value pairs.

        - **Args**:
            - `types` (Optional[List[Type[Agent]]], optional): Types of agents to filter for. Defaults to None.
            - `keys` (Optional[List[str]], optional): Keys to match in agent attributes. Defaults to None.
            - `values` (Optional[List[Any]], optional): Values corresponding to keys for matching. Defaults to None.

        - **Raises**:
            - `ValueError`: If neither types nor keys and values are provided, or if the lengths of keys and values do not match.

        - **Returns**:
            - `List[str]`: A list of filtered agent UUIDs.
        """
        if not types and not keys and not values:
            return self._agent_uuids
        group_to_filter = []
        if types is not None:
            for t in types:
                if t in self._type2group:
                    group_to_filter.extend(self._type2group[t])
                else:
                    raise ValueError(f"type {t} not found in simulation")
        filtered_uuids = []
        if keys:
            if values is None or len(keys) != len(values):
                raise ValueError("the length of key and value does not match")
            for group in group_to_filter:
                filtered_uuids.extend(await group.filter.remote(types, keys, values))
            return filtered_uuids
        else:
            for group in group_to_filter:
                filtered_uuids.extend(await group.filter.remote(types))
            return filtered_uuids

    async def update_environment(self, key: str, value: str):
        """
        Update the environment variables for the simulation and all agent groups.

        - **Args**:
            - `key` (str): The environment variable key to update.
            - `value` (str): The new value for the environment variable.
        """
        self._simulator.update_environment(key, value)
        for group in self._groups.values():
            await group.update_environment.remote(key, value)

    async def update(self, target_agent_uuid: str, target_key: str, content: Any):
        """
        Update the memory of a specified agent.

        - **Args**:
            - `target_agent_uuid` (str): The UUID of the target agent to update.
            - `target_key` (str): The key in the agent's memory to update.
            - `content` (Any): The new content to set for the target key.
        """
        group = self._agent_uuid2group[target_agent_uuid]
        await group.update.remote(target_agent_uuid, target_key, content)

    async def economy_update(
        self,
        target_agent_id: int,
        target_key: str,
        content: Any,
        mode: Literal["replace", "merge"] = "replace",
    ):
        """
        Update economic data for a specified agent.

        - **Args**:
            - `target_agent_id` (int): The ID of the target agent whose economic data to update.
            - `target_key` (str): The key in the agent's economic data to update.
            - `content` (Any): The new content to set for the target key.
            - `mode` (Literal["replace", "merge"], optional): Mode of updating the economic data. Defaults to "replace".
        """
        await self.economy_client.update(
            id=target_agent_id, key=target_key, value=content, mode=mode
        )

    async def send_survey(self, survey: Survey, agent_uuids: list[str] = []):
        """
        Send a survey to specified agents.

        - **Args**:
            - `survey` (Survey): The survey object to send.
            - `agent_uuids` (List[str], optional): List of agent UUIDs to receive the survey. Defaults to an empty list.

        - **Returns**:
            - None
        """
        survey_dict = survey.to_dict()
        _date_time = datetime.now(timezone.utc)
        payload = {
            "from": SURVEY_SENDER_UUID,
            "survey_id": survey_dict["id"],
            "timestamp": int(_date_time.timestamp() * 1000),
            "data": survey_dict,
            "_date_time": _date_time,
        }
        for uuid in agent_uuids:
            topic = self._user_survey_topics[uuid]
            await self.messager.send_message.remote(topic, payload)  # type:ignore
        remain_payback = len(agent_uuids)
        while True:
            messages = await self.messager.fetch_messages.remote()  # type:ignore
            logger.info(f"Received {len(messages)} payback messages [survey]")
            remain_payback -= len(messages)
            if remain_payback <= 0:
                break
            await asyncio.sleep(3)

    async def send_interview_message(
        self, content: str, agent_uuids: Union[str, list[str]]
    ):
        """
        Send an interview message to specified agents.

        - **Args**:
            - `content` (str): The content of the message to send.
            - `agent_uuids` (Union[str, List[str]]): A single UUID string or a list of UUID strings for the agents to receive the message.

        - **Returns**:
            - None
        """
        _date_time = datetime.now(timezone.utc)
        payload = {
            "from": SURVEY_SENDER_UUID,
            "content": content,
            "timestamp": int(_date_time.timestamp() * 1000),
            "_date_time": _date_time,
        }
        if not isinstance(agent_uuids, list):
            agent_uuids = [agent_uuids]
        for uuid in agent_uuids:
            topic = self._user_chat_topics[uuid]
            await self.messager.send_message.remote(topic, payload)  # type:ignore
        remain_payback = len(agent_uuids)
        while True:
            messages = await self.messager.fetch_messages.remote()  # type:ignore
            logger.info(f"Received {len(messages)} payback messages [interview]")
            remain_payback -= len(messages)
            if remain_payback <= 0:
                break
            await asyncio.sleep(3)

    async def extract_metric(self, metric_extractors: list[Callable]):
        """
        Extract metrics using provided extractors.

        - **Description**:
            - Asynchronously applies each metric extractor function to the simulation to collect various metrics.

        - **Args**:
            - `metric_extractors` (List[Callable]): A list of callable functions that take the simulation instance as an argument and return a metric or perform some form of analysis.

        - **Returns**:
            - None
        """
        for metric_extractor in metric_extractors:
            await metric_extractor(self)

    async def step(self):
        """
        Execute one step of the simulation where each agent performs its forward action.

        - **Description**:
            - Checks if new agents need to be inserted based on the current day of the simulation. If so, it inserts them.
            - Executes the forward method for each agent group to advance the simulation by one step.
            - Saves the state of all agent groups after the step has been completed.
            - Optionally extracts metrics if the current step matches the interval specified for any metric extractors.

        - **Raises**:
            - `RuntimeError`: If there is an error during the execution of the step, it logs the error and rethrows it as a RuntimeError.

        - **Returns**:
            - None
        """
        try:
            # step
            simulator_day = await self._simulator.get_simulator_day()
            simulator_time = int(
                await self._simulator.get_simulator_second_from_start_of_day()
            )
            logger.info(
                f"Start simulation day {simulator_day} at {simulator_time}, step {self._total_steps}"
            )
            tasks = []
            for group in self._groups.values():
                tasks.append(group.step.remote())
            log_messages_groups = await asyncio.gather(*tasks)
            llm_log_list = []
            mqtt_log_list = []
            simulator_log_list = []
            agent_time_log_list = []
            for log_messages_group in log_messages_groups:
                llm_log_list.extend(log_messages_group["llm_log"])
                mqtt_log_list.extend(log_messages_group["mqtt_log"])
                simulator_log_list.extend(log_messages_group["simulator_log"])
                agent_time_log_list.extend(log_messages_group["agent_time_log"])
            # save
            simulator_day = await self._simulator.get_simulator_day()
            simulator_time = int(
                await self._simulator.get_simulator_second_from_start_of_day()
            )
            save_tasks = []
            for group in self._groups.values():
                save_tasks.append(group.save.remote(simulator_day, simulator_time))
            await asyncio.gather(*save_tasks)
            self._total_steps += 1
            if self.metric_extractors is not None:  # type:ignore
                to_excute_metric = [
                    metric[1]
                    for metric in self.metric_extractors  # type:ignore
                    if self._total_steps % metric[0] == 0
                ]
                await self.extract_metric(to_excute_metric)

            return llm_log_list, mqtt_log_list, simulator_log_list, agent_time_log_list
        except Exception as e:
            import traceback

            logger.error(f"Simulation error: {str(e)}\n{traceback.format_exc()}")
            raise RuntimeError(str(e)) from e

    async def run(
        self,
        day: int = 1,
    ):
        """
        Run the simulation for a specified number of days.

        - **Args**:
            - `day` (int, optional): The number of days to run the simulation. Defaults to 1.

        - **Description**:
            - Updates the experiment status to running and sets up monitoring for the experiment's status.
            - Runs the simulation loop until the end time, which is calculated based on the current time and the number of days to simulate.
            - After completing the simulation, updates the experiment status to finished, or to failed if an exception occurs.

        - **Raises**:
            - `RuntimeError`: If there is an error during the simulation, it logs the error and updates the experiment status to failed before rethrowing the exception.

        - **Returns**:
            - None
        """
        llm_log_lists = []
        mqtt_log_lists = []
        simulator_log_lists = []
        agent_time_log_lists = []
        try:
            self._exp_info["num_day"] += day
            await self._update_exp_status(1)  # Update status to running

            # Create stop event
            stop_event = asyncio.Event()
            # Create monitor task
            monitor_task = asyncio.create_task(self._monitor_exp_status(stop_event))

            try:
                end_day = self._simulator_day + day
                while True:
                    current_day = await self._simulator.get_simulator_day()
                    if current_day > self._simulator_day:
                        self._simulator_day = current_day
                    if current_day >= end_day:  # type:ignore
                        break
                    (
                        llm_log_list,
                        mqtt_log_list,
                        simulator_log_list,
                        agent_time_log_list,
                    ) = await self.step()
                    llm_log_lists.extend(llm_log_list)
                    mqtt_log_lists.extend(mqtt_log_list)
                    simulator_log_lists.extend(simulator_log_list)
                    agent_time_log_lists.extend(agent_time_log_list)
            finally:
                # Set stop event
                stop_event.set()
                # Wait for monitor task to finish
                await monitor_task

            # Update experiment status after successful run
            await self._update_exp_status(2)
            return (
                llm_log_lists,
                mqtt_log_lists,
                simulator_log_lists,
                agent_time_log_lists,
            )
        except Exception as e:
            error_msg = f"Simulation error: {str(e)}"
            logger.error(error_msg)
            await self._update_exp_status(3, error_msg)
            raise RuntimeError(error_msg) from e
