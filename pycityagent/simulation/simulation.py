import asyncio
import json
import logging
import os
import random
import time
import uuid
from collections.abc import Callable, Sequence
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional, Union

import pycityproto.city.economy.v2.economy_pb2 as economyv2
import ray
import yaml
from langchain_core.embeddings import Embeddings
from mosstool.map._map_util.const import AOI_START_ID

from ..agent import Agent, InstitutionAgent
from ..environment.simulator import Simulator
from ..llm import SimpleEmbedding
from ..memory import FaissQuery, Memory
from ..message.messager import Messager
from ..metrics import init_mlflow_connection
from ..survey import Survey
from .agentgroup import AgentGroup
from .storage.pg import PgWriter, create_pg_tables

logger = logging.getLogger("pycityagent")


class AgentSimulation:
    """城市智能体模拟器"""

    def __init__(
        self,
        agent_class: Union[type[Agent], list[type[Agent]]],
        config: dict,
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
        else:
            self.agent_class = [agent_class]
        self.logging_level = logging_level
        self.config = config
        self.exp_name = exp_name
        self._simulator = Simulator(config["simulator_request"])
        self.agent_prefix = agent_prefix
        self._agents: dict[uuid.UUID, Agent] = {}
        self._groups: dict[str, AgentGroup] = {}  # type:ignore
        self._agent_uuid2group: dict[uuid.UUID, AgentGroup] = {}  # type:ignore
        self._agent_uuids: list[uuid.UUID] = []
        self._user_chat_topics: dict[uuid.UUID, str] = {}
        self._user_survey_topics: dict[uuid.UUID, str] = {}
        self._user_interview_topics: dict[uuid.UUID, str] = {}
        self._loop = asyncio.get_event_loop()
        # self._last_asyncio_pg_task = None  # 将SQL写入的IO隐藏到计算任务后

        self._messager = Messager(
            hostname=config["simulator_request"]["mqtt"]["server"],
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
            self._pgsql_dsn = _pgsql_config["data_source_name"]

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
    def agents(self) -> dict[uuid.UUID, Agent]:
        return self._agents

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

    def create_remote_group(
        self,
        group_name: str,
        agents: list[Agent],
        config: dict,
        exp_id: str,
        exp_name: str,
        enable_avro: bool,
        avro_path: Path,
        enable_pgsql: bool,
        pgsql_writer: ray.ObjectRef,
        mlflow_run_id: str = None,  # type: ignore
        embedding_model: Embeddings = None,  # type: ignore
        logging_level: int = logging.WARNING,
    ):
        """创建远程组"""
        group = AgentGroup.remote(
            agents,
            config,
            exp_id,
            exp_name,
            enable_avro,
            avro_path,
            enable_pgsql,
            pgsql_writer,
            mlflow_run_id,
            embedding_model,
            logging_level,
        )
        return group_name, group, agents

    async def init_agents(
        self,
        agent_count: Union[int, list[int]],
        group_size: int = 1000,
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
        await self._messager.connect()
        if not isinstance(agent_count, list):
            agent_count = [agent_count]

        if len(self.agent_class) != len(agent_count):
            raise ValueError("agent_class和agent_count的长度不一致")

        if memory_config_func is None:
            logger.warning(
                "memory_config_func is None, using default memory config function"
            )
            memory_config_func = []
            for agent_class in self.agent_class:
                if issubclass(agent_class, InstitutionAgent):
                    memory_config_func.append(self.default_memory_config_institution)
                else:
                    memory_config_func.append(self.default_memory_config_citizen)
        elif not isinstance(memory_config_func, list):
            memory_config_func = [memory_config_func]

        if len(memory_config_func) != len(agent_count):
            logger.warning(
                "memory_config_func和agent_count的长度不一致，使用默认的memory_config"
            )
            memory_config_func = []
            for agent_class in self.agent_class:
                if issubclass(agent_class, InstitutionAgent):
                    memory_config_func.append(self.default_memory_config_institution)
                else:
                    memory_config_func.append(self.default_memory_config_citizen)
        # 使用线程池并行创建 AgentGroup
        group_creation_params = []
        class_init_index = 0

        # 首先收集所有需要创建的组的参数
        for i in range(len(self.agent_class)):
            agent_class = self.agent_class[i]
            agent_count_i = agent_count[i]
            memory_config_func_i = memory_config_func[i]
            for j in range(agent_count_i):
                agent_name = f"{self.agent_prefix}_{i}_{j}"

                # 获取Memory配置
                extra_attributes, profile, base = memory_config_func_i()
                memory = Memory(config=extra_attributes, profile=profile, base=base)

                # 创建智能体时传入Memory配置
                agent = agent_class(
                    name=agent_name,
                    memory=memory,
                )

                self._agents[agent._uuid] = agent  # type:ignore
                self._agent_uuids.append(agent._uuid)  # type:ignore

            # 计算需要的组数,向上取整以处理不足一组的情况
            num_group = (agent_count_i + group_size - 1) // group_size

            for k in range(num_group):
                start_idx = class_init_index + k * group_size
                end_idx = min(
                    class_init_index + (k + 1) * group_size,  # 修正了索引计算
                    class_init_index + agent_count_i,
                )

                agents = list(self._agents.values())[start_idx:end_idx]
                group_name = f"AgentType_{i}_Group_{k}"

                # 收集创建参数
                group_creation_params.append((group_name, agents))

            class_init_index += agent_count_i

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
        # 收集所有创建组的参数
        creation_tasks = []
        for i, (group_name, agents) in enumerate(group_creation_params):
            # 直接创建异步任务
            group = AgentGroup.remote(
                agents,
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
            )
            creation_tasks.append((group_name, group, agents))

        # 更新数据结构
        for group_name, group, agents in creation_tasks:
            self._groups[group_name] = group
            for agent in agents:
                self._agent_uuid2group[agent._uuid] = group

        # 并行初始化所有组的agents
        init_tasks = []
        for group in self._groups.values():
            init_tasks.append(group.init_agents.remote())
        await asyncio.gather(*init_tasks)

        # 设置用户主题
        for uuid, agent in self._agents.items():
            self._user_chat_topics[uuid] = f"exps/{self.exp_id}/agents/{uuid}/user-chat"
            self._user_survey_topics[uuid] = (
                f"exps/{self.exp_id}/agents/{uuid}/user-survey"
            )

    async def gather(self, content: str):
        """收集智能体的特定信息"""
        gather_tasks = []
        for group in self._groups.values():
            gather_tasks.append(group.gather.remote(content))
        return await asyncio.gather(*gather_tasks)

    async def update(self, target_agent_uuid: uuid.UUID, target_key: str, content: Any):
        """更新指定智能体的记忆"""
        group = self._agent_uuid2group[target_agent_uuid]
        await group.update.remote(target_agent_uuid, target_key, content)

    def default_memory_config_institution(self):
        """默认的Memory配置函数"""
        EXTRA_ATTRIBUTES = {
            "type": (
                int,
                random.choice(
                    [
                        economyv2.ORG_TYPE_BANK,
                        economyv2.ORG_TYPE_GOVERNMENT,
                        economyv2.ORG_TYPE_FIRM,
                        economyv2.ORG_TYPE_NBS,
                        economyv2.ORG_TYPE_UNSPECIFIED,
                    ]
                ),
            ),
            "nominal_gdp": (list, [], True),
            "real_gdp": (list, [], True),
            "unemployment": (list, [], True),
            "wages": (list, [], True),
            "prices": (list, [], True),
            "inventory": (int, 0, True),
            "price": (float, 0.0, True),
            "interest_rate": (float, 0.0, True),
            "bracket_cutoffs": (list, [], True),
            "bracket_rates": (list, [], True),
            "employees": (list, [], True),
            "customers": (list, [], True),
        }
        return EXTRA_ATTRIBUTES, None, None

    def default_memory_config_citizen(self):
        """默认的Memory配置函数"""
        EXTRA_ATTRIBUTES = {
            # 需求信息
            "needs": (
                dict,
                {
                    "hungry": random.random(),  # 饥饿感
                    "tired": random.random(),  # 疲劳感
                    "safe": random.random(),  # 安全需
                    "social": random.random(),  # 社会需求
                },
                True,
            ),
            "current_need": (str, "none", True),
            "current_plan": (list, [], True),
            "current_step": (dict, {"intention": "", "type": ""}, True),
            "execution_context": (dict, {}, True),
            "plan_history": (list, [], True),
            # cognition
            "fulfillment": (int, 5, True),
            "emotion": (int, 5, True),
            "attitude": (int, 5, True),
            "thought": (str, "Currently nothing good or bad is happening", True),
            "emotion_types": (str, "Relief", True),
            "incident": (list, [], True),
            # social
            "friends": (list, [], True),
        }

        PROFILE = {
            "name": "unknown",
            "gender": random.choice(["male", "female"]),
            "education": random.choice(
                ["Doctor", "Master", "Bachelor", "College", "High School"]
            ),
            "consumption": random.choice(["sightly low", "low", "medium", "high"]),
            "occupation": random.choice(
                [
                    "Student",
                    "Teacher",
                    "Doctor",
                    "Engineer",
                    "Manager",
                    "Businessman",
                    "Artist",
                    "Athlete",
                    "Other",
                ]
            ),
            "age": random.randint(18, 65),
            "skill": random.choice(
                [
                    "Good at problem-solving",
                    "Good at communication",
                    "Good at creativity",
                    "Good at teamwork",
                    "Other",
                ]
            ),
            "family_consumption": random.choice(["low", "medium", "high"]),
            "personality": random.choice(
                ["outgoint", "introvert", "ambivert", "extrovert"]
            ),
            "income": str(random.randint(1000, 10000)),
            "currency": random.randint(10000, 100000),
            "residence": random.choice(["city", "suburb", "rural"]),
            "race": random.choice(
                [
                    "Chinese",
                    "American",
                    "British",
                    "French",
                    "German",
                    "Japanese",
                    "Korean",
                    "Russian",
                    "Other",
                ]
            ),
            "religion": random.choice(
                ["none", "Christian", "Muslim", "Buddhist", "Hindu", "Other"]
            ),
            "marital_status": random.choice(
                ["not married", "married", "divorced", "widowed"]
            ),
        }

        BASE = {
            "home": {
                "aoi_position": {"aoi_id": AOI_START_ID + random.randint(1, 50000)}
            },
            "work": {
                "aoi_position": {"aoi_id": AOI_START_ID + random.randint(1, 50000)}
            },
        }

        return EXTRA_ATTRIBUTES, PROFILE, BASE

    async def send_survey(
        self, survey: Survey, agent_uuids: Optional[list[uuid.UUID]] = None
    ):
        """发送问卷"""
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
            await self._messager.send_message(topic, payload)

    async def send_interview_message(
        self, content: str, agent_uuids: Union[uuid.UUID, list[uuid.UUID]]
    ):
        """发送面试消息"""
        _date_time = datetime.now(timezone.utc)
        payload = {
            "from": "none",
            "content": content,
            "timestamp": int(_date_time.timestamp() * 1000),
            "_date_time": _date_time,
        }
        if not isinstance(agent_uuids, Sequence):
            agent_uuids = [agent_uuids]
        for uuid in agent_uuids:
            topic = self._user_chat_topics[uuid]
            await self._messager.send_message(topic, payload)

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
                pg_exp_info = {k: v for k, v in self._exp_info.items()}
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
            raise e

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
