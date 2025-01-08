import asyncio
import json
import logging
import time
import uuid
from collections.abc import Callable, Sequence
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional, Type, Union

import ray
import yaml
from langchain_core.embeddings import Embeddings

from ..agent import Agent, InstitutionAgent
from ..environment.simulator import Simulator
from ..llm import SimpleEmbedding
from ..memory import Memory
from ..message.messager import Messager
from ..metrics import init_mlflow_connection
from ..survey import Survey
from ..utils import TO_UPDATE_EXP_INFO_KEYS_AND_TYPES
from .agentgroup import AgentGroup
from .storage.pg import PgWriter, create_pg_tables
from ..cityagent import SocietyAgent, FirmAgent, BankAgent, NBSAgent, GovernmentAgent, memory_config_societyagent, memory_config_government, memory_config_firm, memory_config_bank, memory_config_nbs
from ..cityagent.initial import bind_agent_info, initialize_social_network

logger = logging.getLogger("pycityagent")

class AgentSimulation:
    """城市智能体模拟器"""

    def __init__(
        self,
        config: dict,
        agent_class: Union[None, type[Agent], list[type[Agent]]] = None,
        agent_config_file: Optional[dict] = None,
        enable_economy: bool = True,
        agent_prefix: str = "agent_",
        exp_name: str = "default_experiment",
        logging_level: int = logging.WARNING,
    ):
        """
        Args:
            agent_class: 智能体类
            config: 配置
            agent_prefix: 智能体名称前缀
            exp_name: 实验名称
        """
        self.exp_id = str(uuid.uuid4())
        if isinstance(agent_class, list):
            self.agent_class = agent_class
        elif agent_class is None:
            if enable_economy:
                self.agent_class = [SocietyAgent, FirmAgent, BankAgent, NBSAgent, GovernmentAgent]
                self.default_memory_config_func = [
                    memory_config_societyagent,
                    memory_config_firm,
                    memory_config_bank,
                    memory_config_nbs,
                    memory_config_government,
                ]
            else:
                self.agent_class = [SocietyAgent]
                self.default_memory_config_func = [memory_config_societyagent]
        else:
            self.agent_class = [agent_class]
        self.agent_config_file = agent_config_file
        self.logging_level = logging_level
        self.config = config
        self.exp_name = exp_name
        self._simulator = Simulator(config["simulator_request"])
        self.agent_prefix = agent_prefix
        self._groups: dict[str, AgentGroup] = {}  # type:ignore
        self._agent_uuid2group: dict[str, AgentGroup] = {}  # type:ignore
        self._agent_uuids: list[str] = []
        self._type2group: dict[Type[Agent], AgentGroup] = {}
        self._user_chat_topics: dict[str, str] = {}
        self._user_survey_topics: dict[str, str] = {}
        self._user_interview_topics: dict[str, str] = {}
        self._loop = asyncio.get_event_loop()
        # self._last_asyncio_pg_task = None  # 将SQL写入的IO隐藏到计算任务后

        self._messager = Messager.remote(
            hostname=config["simulator_request"]["mqtt"]["server"], # type:ignore
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
        - agent_config: 
            - agent_config_file: Optional[dict]
            - memory_config_func: Optional[Union[Callable, list[Callable]]]
            - init_func: Optional[list[Callable[AgentSimulation, None]]]
            - group_size: Optional[int]
            - embedding_model: Optional[EmbeddingModel]
            - number_of_citizen: required, int
            - number_of_firm: required, int
            - number_of_government: required, int
            - number_of_bank: required, int
            - number_of_nbs: required, int
        - workflow:
            - list[Step]
            - Step:
                - type: str, "step", "run", "interview", "survey", "intervene"
                - day: int if type is "run", else None
                - time: int if type is "step", else None
                - description: Optional[str], description of the step
                - step_func: Optional[Callable[AgentSimulation, None]], only used when type is "interview", "survey" and "intervene"
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
            exp_name=config.get("exp_name", "default_experiment"),
            logging_level=config.get("logging_level", logging.WARNING),
        )
        logger.info("Initializing Agents...")
        agent_count = []
        agent_count.append(config["agent_config"]["number_of_citizen"])
        agent_count.append(config["agent_config"]["number_of_firm"])
        agent_count.append(config["agent_config"]["number_of_government"])
        agent_count.append(config["agent_config"]["number_of_bank"])
        agent_count.append(config["agent_config"]["number_of_nbs"])
        await simulation.init_agents(
            agent_count=agent_count,
            group_size=config["agent_config"].get("group_size", 10000),
            embedding_model=config["agent_config"].get("embedding_model", SimpleEmbedding()),
            memory_config_func=config["agent_config"].get("memory_config_func", None),
        )
        logger.info("Running Init Functions...")
        for init_func in config["agent_config"].get("init_func", [bind_agent_info, initialize_social_network]):
            await init_func(simulation)
        logger.info("Starting Simulation...")
        for step in config["workflow"]:
            logger.info(f"Running step: type: {step['type']} - description: {step.get('description', 'no description')}")
            if step["type"] not in ["run", "step", "interview", "survey", "intervene"]:
                raise ValueError(f"Invalid step type: {step['type']}")
            if step["type"] == "run":
                await simulation.run(step.get("day", 1))
            elif step["type"] == "step":
                await simulation.step(step.get("time", 1))
            else:
                await step["step_func"](simulation)
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
    def groups(self):
        return self._groups

    @property
    def agent_uuids(self):
        return self._agent_uuids

    @property
    def agent_uuid2group(self):
        return self._agent_uuid2group
    
    @property
    def messager(self):
        return self._messager
    
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

    async def init_agents(
        self,
        agent_count: Union[int, list[int]],
        group_size: int = 10000,
        pg_sql_writers: int = 32,
        embedding_model: Embeddings = SimpleEmbedding(),
        memory_config_func: Optional[Union[Callable, list[Callable]]] = None,
    ) -> None:
        """初始化智能体

        Args:
            agent_count: 要创建的总智能体数量, 如果为列表，则每个元素表示一个智能体类创建的智能体数量
            group_size: 每个组的智能体数量，每一个组为一个独立的ray actor
            memory_config_func: 返回Memory配置的函数，需要返回(EXTRA_ATTRIBUTES, PROFILE, BASE)元组, 如果为列表，则每个元素表示一个智能体类创建的Memory配置函数
        """
        if not isinstance(agent_count, list):
            agent_count = [agent_count]

        if len(self.agent_class) != len(agent_count):
            raise ValueError("agent_class和agent_count的长度不一致")

        if memory_config_func is None:
            logger.warning(
                "memory_config_func is None, using default memory config function"
            )
            memory_config_func = self.default_memory_config_func

        elif not isinstance(memory_config_func, list):
            memory_config_func = [memory_config_func]

        if len(memory_config_func) != len(agent_count):
            logger.warning(
                "The length of memory_config_func and agent_count does not match, using default memory_config"
            )
            memory_config_func = self.default_memory_config_func
        # 使用线程池并行创建 AgentGroup
        group_creation_params = []

        # 分别处理机构智能体和普通智能体
        institution_params = []
        citizen_params = []
        
        # 收集所有参数
        for i in range(len(self.agent_class)):
            agent_class = self.agent_class[i]
            agent_count_i = agent_count[i]
            memory_config_func_i = memory_config_func[i]
            
            if self.agent_config_file is not None:
                config_file = self.agent_config_file.get(agent_class, None) 
            else:
                config_file = None
                
            if issubclass(agent_class, InstitutionAgent):
                institution_params.append((agent_class, agent_count_i, memory_config_func_i, config_file))
            else:
                citizen_params.append((agent_class, agent_count_i, memory_config_func_i, config_file))

        # 处理机构智能体组
        if institution_params:
            total_institution_count = sum(p[1] for p in institution_params)
            num_institution_groups = (total_institution_count + group_size - 1) // group_size
            
            for k in range(num_institution_groups):
                start_idx = k * group_size
                remaining = total_institution_count - start_idx
                number_of_agents = min(remaining, group_size)
                
                agent_classes = []
                agent_counts = []
                memory_config_funcs = []
                config_files = []
                
                # 分配每种类型的机构智能体到当前组
                curr_start = start_idx
                for agent_class, count, mem_func, conf_file in institution_params:
                    if curr_start < count:
                        agent_classes.append(agent_class)
                        agent_counts.append(min(count - curr_start, number_of_agents))
                        memory_config_funcs.append(mem_func)
                        config_files.append(conf_file)
                    curr_start = max(0, curr_start - count)
                
                group_creation_params.append((
                    agent_classes,
                    agent_counts, 
                    memory_config_funcs,
                    f"InstitutionGroup_{k}",
                    config_files
                ))

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
                memory_config_funcs = []
                config_files = []
                
                # 分配每种类型的普通智能体到当前组
                curr_start = start_idx
                for agent_class, count, mem_func, conf_file in citizen_params:
                    if curr_start < count:
                        agent_classes.append(agent_class)
                        agent_counts.append(min(count - curr_start, number_of_agents))
                        memory_config_funcs.append(mem_func)
                        config_files.append(conf_file)
                    curr_start = max(0, curr_start - count)
                
                group_creation_params.append((
                    agent_classes,
                    agent_counts,
                    memory_config_funcs, 
                    f"CitizenGroup_{k}",
                    config_files
                ))

        # 初始化mlflow连接
        _mlflow_config = self.config.get("metric_request", {}).get("mlflow")
        if _mlflow_config:
            mlflow_run_id, _ = init_mlflow_connection(
                config=_mlflow_config,
                mlflow_run_name=f"EXP_{self.exp_name}_{1000*int(time.time())}",
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

        creation_tasks = []
        for i, (agent_class, number_of_agents, memory_config_function_group, group_name, config_file) in enumerate(group_creation_params):
            # 直接创建异步任务
            group = AgentGroup.remote(
                agent_class,
                number_of_agents,
                memory_config_function_group,
                self.config,
                self.exp_id,
                self.exp_name,
                self.enable_avro,
                self.avro_path,
                self.enable_pgsql,
                _workers[i % _num_workers],  # type:ignore
                mlflow_run_id,  # type:ignore
                embedding_model,
                self.logging_level,
                config_file,
            )
            creation_tasks.append((group_name, group))

        # 更新数据结构
        for group_name, group in creation_tasks:
            self._groups[group_name] = group
            group_agent_uuids = ray.get(group.get_agent_uuids.remote())
            for agent_uuid in group_agent_uuids:
                self._agent_uuid2group[agent_uuid] = group
                self._user_chat_topics[agent_uuid] = f"exps/{self.exp_id}/agents/{agent_uuid}/user-chat"
                self._user_survey_topics[agent_uuid] = (
                    f"exps/{self.exp_id}/agents/{agent_uuid}/user-survey"
                )
            group_agent_type = ray.get(group.get_agent_type.remote())
            for agent_type in group_agent_type:
                if agent_type not in self._type2group:
                    self._type2group[agent_type] = []
                self._type2group[agent_type].append(group)

        # 并行初始化所有组的agents
        init_tasks = []
        for group in self._groups.values():
            init_tasks.append(group.init_agents.remote())
        ray.get(init_tasks)

    async def gather(self, content: str):
        """收集智能体的特定信息"""
        gather_tasks = []
        for group in self._groups.values():
            gather_tasks.append(group.gather.remote(content))
        return await asyncio.gather(*gather_tasks)
    
    async def filter(self, 
                     types: Optional[list[Type[Agent]]] = None, 
                     keys: Optional[list[str]] = None, 
                     values: Optional[list[Any]] = None) -> list[str]:
        """过滤出指定类型的智能体"""
        if not types and not keys and not values:
            return self._agent_uuids
        group_to_filter = []
        for t in types:
            if t in self._type2group:
                group_to_filter.extend(self._type2group[t])
            else:
                raise ValueError(f"type {t} not found in simulation")
        filtered_uuids = []
        if keys:
            if len(keys) != len(values):
                raise ValueError("the length of key and value does not match")
            for group in group_to_filter:
                filtered_uuids.extend(await group.filter.remote(types, keys, values))
            return filtered_uuids
        else:
            for group in group_to_filter:
                filtered_uuids.extend(await group.filter.remote(types))
            return filtered_uuids

    async def update(self, target_agent_uuid: str, target_key: str, content: Any):
        """更新指定智能体的记忆"""
        group = self._agent_uuid2group[target_agent_uuid]
        await group.update.remote(target_agent_uuid, target_key, content)

    async def send_survey(
        self, survey: Survey, agent_uuids: Optional[list[str]] = None
    ):
        """发送问卷"""
        await self.messager.connect()
        survey_dict = survey.to_dict()
        if agent_uuids is None:
            agent_uuids = self._agent_uuids
        _date_time = datetime.now(timezone.utc)
        payload = {
            "from": "none",
            "survey_id": survey_dict["id"],
            "timestamp": int(_date_time.timestamp() * 1000),
            "data": survey_dict,
            "_date_time": _date_time,
        }
        for uuid in agent_uuids:
            topic = self._user_survey_topics[uuid]
            await self.messager.send_message(topic, payload)

    async def send_interview_message(
        self, content: str, agent_uuids: Union[str, list[str]]
    ):
        """发送采访消息"""
        await self.messager.connect()
        _date_time = datetime.now(timezone.utc)
        payload = {
            "from": "none",
            "content": content,
            "timestamp": int(_date_time.timestamp() * 1000),
            "_date_time": _date_time,
        }
        if not isinstance(agent_uuids, list):
            agent_uuids = [agent_uuids]
        for uuid in agent_uuids:
            topic = self._user_chat_topics[uuid]
            await self.messager.send_message(topic, payload)

    async def step(self):
        """运行一步, 即每个智能体执行一次forward"""
        try:
            tasks = []
            for group in self._groups.values():
                tasks.append(group.step.remote())
            await asyncio.gather(*tasks)
        except Exception as e:
            logger.error(f"运行错误: {str(e)}")
            raise

    async def run(
        self,
        day: int = 1,
    ):
        """运行模拟器"""
        try:
            self._exp_info["num_day"] += day
            await self._update_exp_status(1)  # 更新状态为运行中

            # 创建停止事件
            stop_event = asyncio.Event()
            # 创建监控任务
            monitor_task = asyncio.create_task(self._monitor_exp_status(stop_event))

            try:
                for _ in range(day):
                    tasks = []
                    for group in self._groups.values():
                        tasks.append(group.run.remote())
                    # 等待所有group运行完成
                    await asyncio.gather(*tasks)

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
