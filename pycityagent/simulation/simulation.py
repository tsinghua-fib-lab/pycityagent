import asyncio
import json
import logging
import os
import random
import uuid
from collections.abc import Sequence
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Union

import pycityproto.city.economy.v2.economy_pb2 as economyv2
import yaml
from mosstool.map._map_util.const import AOI_START_ID

from pycityagent.environment.simulator import Simulator
from pycityagent.memory.memory import Memory
from pycityagent.message.messager import Messager
from pycityagent.survey import Survey

from ..agent import Agent, InstitutionAgent
from .agentgroup import AgentGroup

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
        self._simulator = Simulator(config["simulator_request"])
        self.agent_prefix = agent_prefix
        self._agents: Dict[uuid.UUID, Agent] = {}
        self._groups: Dict[str, AgentGroup] = {}  # type:ignore
        self._agent_uuid2group: Dict[uuid.UUID, AgentGroup] = {}  # type:ignore
        self._agent_uuids: List[uuid.UUID] = []
        self._user_chat_topics: Dict[uuid.UUID, str] = {}
        self._user_survey_topics: Dict[uuid.UUID, str] = {}
        self._user_interview_topics: Dict[uuid.UUID, str] = {}
        self._loop = asyncio.get_event_loop()

        self._messager = Messager(
            hostname=config["simulator_request"]["mqtt"]["server"],
            port=config["simulator_request"]["mqtt"]["port"],
            username=config["simulator_request"]["mqtt"].get("username", None),
            password=config["simulator_request"]["mqtt"].get("password", None),
        )
        asyncio.create_task(self._messager.connect())

        self._enable_avro = config["storage"]["avro"]["enabled"]
        if not self._enable_avro:
            logger.warning("AVRO is not enabled, NO AVRO LOCAL STORAGE")
        self._avro_path = Path(config["storage"]["avro"]["path"]) / f"{self.exp_id}"
        self._avro_path.mkdir(parents=True, exist_ok=True)

        self._enable_pgsql = config["storage"]["pgsql"]["enabled"]
        self._pgsql_host = config["storage"]["pgsql"]["host"]
        self._pgsql_port = config["storage"]["pgsql"]["port"]
        self._pgsql_database = config["storage"]["pgsql"]["database"]
        self._pgsql_user = config["storage"]["pgsql"]["user"]
        self._pgsql_password = config["storage"]["pgsql"]["password"]

        # 添加实验信息相关的属性
        self._exp_info = {
            "id": self.exp_id,
            "name": exp_name,
            "num_day": 0,  # 将在 run 方法中更新
            "status": 0,
            "cur_day": 0,
            "cur_t": 0.0,
            "config": json.dumps(config),
            "error": "",
            "created_at": datetime.now(timezone.utc).isoformat(),
        }

        # 创建异步任务保存实验信息
        self._exp_info_file = self._avro_path / "experiment_info.yaml"
        with open(self._exp_info_file, "w") as f:
            yaml.dump(self._exp_info, f)

    @property
    def agents(self):
        return self._agents

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
        enable_avro: bool,
        avro_path: Path,
        logging_level: int = logging.WARNING,
    ):
        """创建远程组"""
        group = AgentGroup.remote(
            agents, config, exp_id, enable_avro, avro_path, logging_level
        )
        return group_name, group, agents

    async def init_agents(
        self,
        agent_count: Union[int, list[int]],
        group_size: int = 1000,
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

                self._agents[agent._uuid] = agent
                self._agent_uuids.append(agent._uuid)

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

        # 收集所有创建组的参数
        creation_tasks = []
        for group_name, agents in group_creation_params:
            # 直接创建异步任务
            group = AgentGroup.remote(
                agents,
                self.config,
                self.exp_id,
                self._enable_avro,
                self._avro_path,
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
        self, survey: Survey, agent_uuids: Optional[List[uuid.UUID]] = None
    ):
        """发送问卷"""
        survey_dict = survey.to_dict()
        if agent_uuids is None:
            agent_uuids = self._agent_uuids
        payload = {
            "from": "none",
            "survey_id": survey_dict["id"],
            "timestamp": int(datetime.now().timestamp() * 1000),
            "data": survey_dict,
        }
        for uuid in agent_uuids:
            topic = self._user_survey_topics[uuid]
            await self._messager.send_message(topic, payload)

    async def send_interview_message(
        self, content: str, agent_uuids: Union[uuid.UUID, List[uuid.UUID]]
    ):
        """发送面试消息"""
        payload = {
            "from": "none",
            "content": content,
            "timestamp": int(datetime.now().timestamp() * 1000),
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
            with open(self._exp_info_file, "w") as f:
                yaml.dump(self._exp_info, f)
        except Exception as e:
            logger.error(f"保存实验信息失败: {str(e)}")

    async def _update_exp_status(self, status: int, error: str = "") -> None:
        """更新实验状态并保存"""
        self._exp_info["status"] = status
        self._exp_info["error"] = error
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
