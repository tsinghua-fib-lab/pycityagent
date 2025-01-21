import asyncio
import json
import logging
import time
import uuid
from collections.abc import Callable
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Literal, Optional, Type, Union

import ray
import yaml
from langchain_core.embeddings import Embeddings

from ..agent import Agent, InstitutionAgent
from ..cityagent import (BankAgent, FirmAgent, GovernmentAgent, NBSAgent,
                         SocietyAgent)
from ..cityagent.memory_config import (memory_config_bank, memory_config_firm,
                         memory_config_government, memory_config_nbs,
                         memory_config_societyagent, memory_config_init)
from ..cityagent.initial import bind_agent_info, initialize_social_network
from ..cityagent.message_intercept import (EdgeMessageBlock,
                                           MessageBlockListener,
                                           PointMessageBlock)
from ..economy.econ_client import EconomyClient
from ..environment import Simulator
from ..llm import SimpleEmbedding
from ..message import (MessageBlockBase, MessageBlockListenerBase,
                       MessageInterceptor, Messager)
from ..metrics import init_mlflow_connection
from ..metrics.mlflow_client import MlflowClient
from ..survey import Survey
from ..utils import SURVEY_SENDER_UUID, TO_UPDATE_EXP_INFO_KEYS_AND_TYPES
from .agentgroup import AgentGroup
from .storage.pg import PgWriter, create_pg_tables

logger = logging.getLogger("pycityagent")

class AgentSimulation:
    """Agent Simulation"""

    def __init__(
        self,
        config: dict,
        agent_class: Union[None, type[Agent], list[type[Agent]]] = None,
        agent_config_file: Optional[dict] = None,
        metric_extractors: Optional[list[tuple[int, Callable]]] = None,
        enable_institution: bool = True,
        agent_prefix: str = "agent_",
        exp_name: str = "default_experiment",
        logging_level: int = logging.WARNING,
    ):
        """
        Args:
            config: Configuration
            agent_class: Agent class
            agent_config_file: Agent configuration file
            metric_extractors: Metric extractor
            enable_institution: Whether to enable institution
            agent_prefix: Agent name prefix
            exp_name: Experiment name
            logging_level: Logging level
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
        self.agent_config_file = agent_config_file
        self.logging_level = logging_level
        self.config = config
        self.exp_name = exp_name
        _simulator_config = config["simulator_request"].get("simulator", {})
        if "server" in _simulator_config:
            raise ValueError(f"Passing Traffic Simulation address is not supported!")
        self._simulator = Simulator(config["simulator_request"])
        self._economy_client = EconomyClient(
            config["simulator_request"]["simulator"]["server"]
        )
        if enable_institution:
            self._economy_addr = economy_addr = self._simulator.server_addr
            if economy_addr is None:
                raise ValueError(
                    f"`simulator` not provided in `simulator_request`, thus unable to activate economy!"
                )
            _req_dict: dict = self.config["simulator_request"]
            if "economy" in _req_dict:
                if _req_dict["economy"] is None:
                    _req_dict["economy"] = {}
                if "server" in _req_dict["economy"]:
                    raise ValueError(
                        f"Passing Economy Simulation address is not supported!"
                    )
                else:
                    _req_dict["economy"]["server"] = economy_addr
            else:
                _req_dict["economy"] = {
                    "server": economy_addr,
                }
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
        # self._last_asyncio_pg_task = None  # 将SQL写入的IO隐藏到计算任务后

        self._messager = Messager.remote(
            hostname=config["simulator_request"]["mqtt"]["server"],  # type:ignore
            port=config["simulator_request"]["mqtt"]["port"],
            username=config["simulator_request"]["mqtt"].get("username", None),
            password=config["simulator_request"]["mqtt"].get("password", None),
        )

        # storage
        _storage_config: dict[str, Any] = config.get("storage", {})
        if _storage_config is None:
            _storage_config = {}

        # avro
        _avro_config: dict[str, Any] = _storage_config.get("avro", {})
        self._enable_avro = _avro_config.get("enabled", False)
        if not self._enable_avro:
            self._avro_path = None
            logger.warning("AVRO is not enabled, NO AVRO LOCAL STORAGE")
        else:
            self._avro_path = Path(_avro_config["path"]) / f"{self.exp_id}"
            self._avro_path.mkdir(parents=True, exist_ok=True)

        # mlflow
        _mlflow_config: dict[str, Any] = config.get("metric_request", {}).get("mlflow")
        if _mlflow_config:
            logger.info(f"-----Creating Mlflow client...")
            mlflow_run_id, _ = init_mlflow_connection(
                config=_mlflow_config,
                experiment_uuid=self.exp_id,
                mlflow_run_name=f"EXP_{self.exp_name}_{1000*int(time.time())}",
                experiment_name=self.exp_name,
            )
            self.mlflow_client = MlflowClient(
                config=_mlflow_config,
                experiment_uuid=self.exp_id,
                mlflow_run_name=f"EXP_{exp_name}_{1000*int(time.time())}",
                experiment_name=exp_name,
                run_id=mlflow_run_id,
            )
            if metric_extractors is not None:
                self.metric_extractors = metric_extractors
        else:
            logger.warning("Mlflow is not enabled, NO MLFLOW STORAGE")
            self.mlflow_client = None
            self.metric_extractors = None

        # pg
        _pgsql_config: dict[str, Any] = _storage_config.get("pgsql", {})
        self._enable_pgsql = _pgsql_config.get("enabled", False)
        if not self._enable_pgsql:
            logger.warning("PostgreSQL is not enabled, NO POSTGRESQL DATABASE STORAGE")
            self._pgsql_dsn = ""
        else:
            self._pgsql_dsn = (
                _pgsql_config["data_source_name"]
                if "data_source_name" in _pgsql_config
                else _pgsql_config["dsn"]
            )

        # 添加实验信息相关的属性
        self._exp_created_time = datetime.now(timezone.utc)
        self._exp_updated_time = datetime.now(timezone.utc)
        self._exp_info = {
            "id": self.exp_id,
            "name": exp_name,
            "num_day": 0,  # 将在 run 方法中更新
            "status": 0,
            "cur_day": 0,
            "cur_t": 0.0,
            "config": json.dumps(config),
            "error": "",
            "created_at": self._exp_created_time.isoformat(),
            "updated_at": self._exp_updated_time.isoformat(),
        }

        # 创建异步任务保存实验信息
        if self._enable_avro:
            assert self._avro_path is not None
            self._exp_info_file = self._avro_path / "experiment_info.yaml"
            with open(self._exp_info_file, "w") as f:
                yaml.dump(self._exp_info, f)

    @classmethod
    async def run_from_config(cls, config: dict):
        """Directly run from config file
        Basic config file should contain:
        - simulation_config: file_path
        - enable_institution: bool, default is True
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
            - default: {'weather': 'The weather is normal', 'crime': 'The crime rate is low', 'pollution': 'The pollution level is low', 'temperature': 'The temperature is normal'}
        - workflow:
            - list[Step]
            - Step:
                - type: str, "step", "run", "interview", "survey", "intervene", "pause", "resume"
                - days: int if type is "run", else None
                - times: int if type is "step", else None
                - description: Optional[str], description of the step
                - func: Optional[Callable[AgentSimulation, None]], only used when type is "interview", "survey" and "intervene"
        - message_intercept
            - mode: "point"|"edge"
            - max_violation_time: Optional[int], default to 3. The maximum time for someone to send bad message before banned. Used only in `point` mode.
        - logging_level: Optional[int]
        - exp_name: Optional[str]
        """
        # required key check
        if "simulation_config" not in config:
            raise ValueError("simulation_config is required")
        if "agent_config" not in config:
            raise ValueError("agent_config is required")
        if "workflow" not in config:
            raise ValueError("workflow is required")
        import yaml

        logger.info("Loading config file...")
        with open(config["simulation_config"], "r") as f:
            simulation_config = yaml.safe_load(f)
        logger.info("Creating AgentSimulation Task...")
        simulation = cls(
            config=simulation_config,
            agent_config_file=config["agent_config"].get("agent_config_file", None),
            metric_extractors=config["agent_config"].get("metric_extractors", None),
            enable_institution=config.get("enable_institution", True),
            exp_name=config.get("exp_name", "default_experiment"),
            logging_level=config.get("logging_level", logging.WARNING),
        )
        environment = config.get(
            "environment", 
            {
                "weather": "The weather is normal", 
                "crime": "The crime rate is low", 
                "pollution": "The pollution level is low", 
                "temperature": "The temperature is normal"
            }
        )
        simulation._simulator.set_environment(environment)
        logger.info("Initializing Agents...")
        agent_count = {
            SocietyAgent: config["agent_config"].get("number_of_citizen", 0),
            FirmAgent: config["agent_config"].get("number_of_firm", 0),
            GovernmentAgent: config["agent_config"].get("number_of_government", 0),
            BankAgent: config["agent_config"].get("number_of_bank", 0),
            NBSAgent: config["agent_config"].get("number_of_nbs", 0),
        }
        if agent_count.get(SocietyAgent, 0) == 0:
            raise ValueError("number_of_citizen is required")
        
        # support MessageInterceptor
        if "message_intercept" in config:
            _intercept_config = config["message_intercept"]
            _mode = _intercept_config.get("mode", "point")
            if _mode == "point":
                _kwargs = {
                    k: v
                    for k, v in _intercept_config.items()
                    if k
                    in {
                        "max_violation_time",
                    }
                }
                _interceptor_blocks = [PointMessageBlock(**_kwargs)]
            elif _mode == "edge":
                _kwargs = {
                    k: v
                    for k, v in _intercept_config.items()
                    if k
                    in {
                        "max_violation_time",
                    }
                }
                _interceptor_blocks = [EdgeMessageBlock(**_kwargs)]
            else:
                raise ValueError(f"Unsupported interception mode `{_mode}!`")
            _message_intercept_kwargs = {
                "message_interceptor_blocks": _interceptor_blocks,
                "message_listener": MessageBlockListener(),
            }
        else:
            _message_intercept_kwargs = {}
        await simulation.init_agents(
            agent_count=agent_count,
            group_size=config["agent_config"].get("group_size", 10000),
            embedding_model=config["agent_config"].get(
                "embedding_model", SimpleEmbedding()
            ),
            memory_config_func=config["agent_config"].get("memory_config_func", None),  
            memory_config_init_func=config["agent_config"].get("memory_config_init_func", None),
            **_message_intercept_kwargs,
            environment=environment,
        )
        logger.info("Running Init Functions...")
        for init_func in config["agent_config"].get(
            "init_func", [bind_agent_info, initialize_social_network]
        ):
            await init_func(simulation)
        logger.info("Starting Simulation...")
        for step in config["workflow"]:
            logger.info(
                f"Running step: type: {step['type']} - description: {step.get('description', 'no description')}"
            )
            if step["type"] not in ["run", "step", "interview", "survey", "intervene"]:
                raise ValueError(f"Invalid step type: {step['type']}")
            if step["type"] == "run":
                await simulation.run(step.get("days", 1))
            elif step["type"] == "step":
                times = step.get("times", 1)
                for _ in range(times):
                    await simulation.step()
            elif step["type"] == "pause":
                await simulation.pause_simulator()
            elif step["type"] == "resume":
                await simulation.resume_simulator()
            else:
                await step["func"](simulation)
        logger.info("Simulation finished")

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
        """异步保存实验信息到YAML文件"""
        try:
            if self.enable_avro:
                with open(self._exp_info_file, "w") as f:
                    yaml.dump(self._exp_info, f)
        except Exception as e:
            logger.error(f"Avro保存实验信息失败: {str(e)}")
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
            logger.error(f"PostgreSQL保存实验信息失败: {str(e)}")

    async def _update_exp_status(self, status: int, error: str = "") -> None:
        self._exp_updated_time = datetime.now(timezone.utc)
        """更新实验状态并保存"""
        self._exp_info["status"] = status
        self._exp_info["error"] = error
        self._exp_info["updated_at"] = self._exp_updated_time.isoformat()
        await self._save_exp_info()

    async def _monitor_exp_status(self, stop_event: asyncio.Event):
        """监控实验状态并更新

        Args:
            stop_event: 用于通知监控任务停止的事件
        """
        try:
            while not stop_event.is_set():
                # 更新实验状态
                # 假设所有group的cur_day和cur_t是同步的，取第一个即可
                self._exp_info["cur_day"] = await self._simulator.get_simulator_day()
                self._exp_info["cur_t"] = (
                    await self._simulator.get_simulator_second_from_start_of_day()
                )
                await self._save_exp_info()

                await asyncio.sleep(1)  # 避免过于频繁的更新
        except asyncio.CancelledError:
            # 正常取消，不需要特殊处理
            pass
        except Exception as e:
            logger.error(f"监控实验状态时发生错误: {str(e)}")
            raise

    async def __aenter__(self):
        """异步上下文管理器入口"""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """异步上下文管理器出口"""
        if exc_type is not None:
            # 如果发生异常，更新状态为错误
            await self._update_exp_status(3, str(exc_val))
        elif self._exp_info["status"] != 3:
            # 如果没有发生异常且状态不是错误，则更新为完成
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
        environment: Optional[dict[str, str]] = None,
    ) -> None:
        """初始化智能体

        Args:
            agent_count: 要创建的总智能体数量, 如果为列表，则每个元素表示一个智能体类创建的智能体数量
            group_size: 每个组的智能体数量，每一个组为一个独立的ray actor
            pg_sql_writers: 独立的PgSQL writer数量
            message_interceptors: message拦截器数量
            memory_config_func: 返回Memory配置的函数，需要返回(EXTRA_ATTRIBUTES, PROFILE, BASE)元组, 每个元素表示一个智能体类创建的Memory配置函数
            environment: 环境变量，用于更新模拟器的环境变量
        """
        self.agent_count = agent_count

        if len(self.agent_class) != len(agent_count):
            raise ValueError("The length of agent_class and agent_count does not match")

        if memory_config_init_func is not None:
            await memory_config_init(self)
        if memory_config_func is None:
            memory_config_func = self.default_memory_config_func  # type:ignore

        # 使用线程池并行创建 AgentGroup
        group_creation_params = []

        # 分别处理机构智能体和普通智能体
        institution_params = []
        citizen_params = []

        # 收集所有参数
        print(self.agent_class)
        print(agent_count)
        for i in range(len(self.agent_class)):
            agent_class = self.agent_class[i]
            agent_count_i = agent_count[agent_class]
            assert memory_config_func is not None
            memory_config_func_i = memory_config_func.get(
                agent_class, self.default_memory_config_func[agent_class]  # type:ignore
            )

            if self.agent_config_file is not None:
                config_file = self.agent_config_file.get(agent_class, None)
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

        # 处理机构智能体组
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

                # 分配每种类型的机构智能体到当前组
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

        # 处理普通智能体组
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

                # 分配每种类型的普通智能体到当前组
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
        # 初始化mlflow连接
        _mlflow_config = self.config.get("metric_request", {}).get("mlflow")
        if _mlflow_config:
            mlflow_run_id, _ = init_mlflow_connection(
                experiment_uuid=self.exp_id,
                config=_mlflow_config,
                mlflow_run_name=f"{self.exp_name}_{1000*int(time.time())}",
                experiment_name=self.exp_name,
            )
        else:
            mlflow_run_id = None
        # 建表
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
        _llm_config = self.config.get("llm_request", {})
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
            # 直接创建异步任务
            group = AgentGroup.remote(
                agent_class,
                number_of_agents,
                memory_config_function_group,
                self.config,
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
                environment,
            )
            creation_tasks.append((group_name, group))

        # 更新数据结构
        for group_name, group in creation_tasks:
            self._groups[group_name] = group
            group_agent_uuids = ray.get(group.get_agent_uuids.remote())
            for agent_uuid in group_agent_uuids:
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

        # 并行初始化所有组的agents
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

    async def gather(
        self, content: str, target_agent_uuids: Optional[list[str]] = None
    ):
        """收集智能体的特定信息"""
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
        """过滤出指定类型的智能体"""
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
        self._simulator.update_environment(key, value)
        for group in self._groups.values():
            await group.update_environment.remote(key, value)

    async def update(self, target_agent_uuid: str, target_key: str, content: Any):
        """更新指定智能体的记忆"""
        group = self._agent_uuid2group[target_agent_uuid]
        await group.update.remote(target_agent_uuid, target_key, content)

    async def economy_update(
        self,
        target_agent_id: int,
        target_key: str,
        content: Any,
        mode: Literal["replace", "merge"] = "replace",
    ):
        """更新指定智能体的经济数据"""
        await self.economy_client.update(
            id=target_agent_id, key=target_key, value=content, mode=mode
        )

    async def send_survey(self, survey: Survey, agent_uuids: list[str] = []):
        """发送问卷"""
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
        """发送采访消息"""
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
        """提取指标"""
        for metric_extractor in metric_extractors:
            await metric_extractor(self)

    async def step(self):
        """Run one step, each agent execute one forward"""
        try:
            # check whether insert agents
            simulator_day = await self._simulator.get_simulator_day()
            need_insert_agents = False
            if simulator_day > self._simulator_day:
                need_insert_agents = True
                self._simulator_day = simulator_day
            if need_insert_agents:
                await self.resume_simulator()
                insert_tasks = []
                for group in self._groups.values():
                    insert_tasks.append(group.insert_agents.remote())
                await asyncio.gather(*insert_tasks)

            # step
            simulator_day = await self._simulator.get_simulator_day()
            simulator_time = int(await self._simulator.get_time())
            logger.info(f"Start simulation day {simulator_day} at {simulator_time}, step {self._total_steps}")
            tasks = []
            for group in self._groups.values():
                tasks.append(group.step.remote())
            await asyncio.gather(*tasks)
            # save
            simulator_day = await self._simulator.get_simulator_day()
            simulator_time = int(await self._simulator.get_time())
            save_tasks = []
            for group in self._groups.values():
                save_tasks.append(group.save.remote(simulator_day, simulator_time))
            await asyncio.gather(*save_tasks)
            self._total_steps += 1
            if self.metric_extractor is not None:
                print(f"total_steps: {self._total_steps}, excute metric")
                to_excute_metric = [
                    metric[1]
                    for metric in self.metric_extractor
                    if self._total_steps % metric[0] == 0
                ]
                await self.extract_metric(to_excute_metric)
        except Exception as e:
            import traceback

            logger.error(f"模拟器运行错误: {str(e)}\n{traceback.format_exc()}")
            raise RuntimeError(str(e)) from e

    async def run(
        self,
        day: int = 1,
    ):
        """Run the simulation by days"""
        try:
            self._exp_info["num_day"] += day
            await self._update_exp_status(1)  # 更新状态为运行中

            # 创建停止事件
            stop_event = asyncio.Event()
            # 创建监控任务
            monitor_task = asyncio.create_task(self._monitor_exp_status(stop_event))

            try:
                end_time = (
                    await self._simulator.get_time() + day * 24 * 3600
                )  # type:ignore
                while True:
                    current_time = await self._simulator.get_time()
                    if current_time >= end_time:  # type:ignore
                        break
                    await self.step()
            finally:
                # 设置停止事件
                stop_event.set()
                # 等待监控任务结束
                await monitor_task

            # 运行成功后更新状态
            await self._update_exp_status(2)

        except Exception as e:
            error_msg = f"模拟器运行错误: {str(e)}"
            logger.error(error_msg)
            await self._update_exp_status(3, error_msg)
            raise RuntimeError(error_msg) from e
