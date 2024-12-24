import asyncio
import json
import logging
import os
from pathlib import Path
import uuid
from datetime import datetime
import random
from typing import Dict, List, Optional, Callable, Union,Any
import fastavro
from mosstool.map._map_util.const import AOI_START_ID
import pycityproto.city.economy.v2.economy_pb2 as economyv2
from pycityagent.memory.memory import Memory
from pycityagent.message.messager import Messager
from pycityagent.survey import Survey
from pycityagent.utils.avro_schema import PROFILE_SCHEMA, DIALOG_SCHEMA, STATUS_SCHEMA, SURVEY_SCHEMA

from ..agent import Agent, InstitutionAgent
from .agentgroup import AgentGroup

logger = logging.getLogger(__name__)


class AgentSimulation:
    """城市智能体模拟器"""

    def __init__(
        self,
        agent_class: Union[type[Agent], list[type[Agent]]],
        config: dict,
        agent_prefix: str = "agent_",
    ):
        """
        Args:
            agent_class: 智能体类
            config: 配置
            agent_prefix: 智能体名称前缀
        """
        self.exp_id = uuid.uuid4()
        if isinstance(agent_class, list):
            self.agent_class = agent_class
        else:
            self.agent_class = [agent_class]
        self.config = config
        self.agent_prefix = agent_prefix
        self._agents: Dict[uuid.UUID, Agent] = {}
        self._groups: Dict[str, AgentGroup] = {}
        self._agent_uuid2group: Dict[uuid.UUID, AgentGroup] = {}
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
        self._avro_path = Path(config["storage"]["avro"]["path"])
        self._avro_file = {
            "profile": self._avro_path / f"{self.exp_id}_profile.avro",
            "dialog": self._avro_path / f"{self.exp_id}_dialog.avro",
            "status": self._avro_path / f"{self.exp_id}_status.avro",
            "survey": self._avro_path / f"{self.exp_id}_survey.avro",
        }

        self._enable_pgsql = config["storage"]["pgsql"]["enabled"]
        self._pgsql_host = config["storage"]["pgsql"]["host"]
        self._pgsql_port = config["storage"]["pgsql"]["port"]
        self._pgsql_database = config["storage"]["pgsql"]["database"]
        self._pgsql_user = config["storage"]["pgsql"]["user"]
        self._pgsql_password = config["storage"]["pgsql"]["password"]

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
            logging.warning(
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
            logging.warning(
                "memory_config_func和agent_count的长度不一致，使用默认的memory_config"
            )
            memory_config_func = []
            for agent_class in self.agent_class:
                if agent_class == InstitutionAgent:
                    memory_config_func.append(self.default_memory_config_institution)
                else:
                    memory_config_func.append(self.default_memory_config_citizen)

        class_init_index = 0
        for i in range(len(self.agent_class)):
            agent_class = self.agent_class[i]
            agent_count_i = agent_count[i]
            memory_config_func_i = memory_config_func[i]
            for j in range(agent_count_i):
                agent_name = f"{self.agent_prefix}_{i}_{j}"

                # 获取Memory配置
                extra_attributes, profile, base = memory_config_func_i()
                memory = Memory(
                    config=extra_attributes, profile=profile, base=base
                )

                # 创建智能体时传入Memory配置
                agent = agent_class(
                    name=agent_name,
                    memory=memory,
                    avro_file=self._avro_file,
                )

                self._agents[agent._uuid] = agent
                self._agent_uuids.append(agent._uuid)

            # 计算需要的组数,向上取整以处理不足一组的情况
            num_group = (agent_count_i + group_size - 1) // group_size

            for k in range(num_group):
                # 计算当前组的起始和结束索引
                start_idx = class_init_index + k * group_size
                end_idx = min(
                    class_init_index + start_idx + group_size,
                    class_init_index + agent_count_i,
                )

                # 获取当前组的agents
                agents = list(self._agents.values())[start_idx:end_idx]
                group_name = f"AgentType_{i}_Group_{k}"
                group = AgentGroup.remote(agents, self.config, self.exp_id, self._avro_file)
                self._groups[group_name] = group
                for agent in agents:
                    self._agent_uuid2group[agent._uuid] = group

            class_init_index += agent_count_i  # 更新类初始索引

        init_tasks = []
        for group in self._groups.values():
            init_tasks.append(group.init_agents.remote())
        await asyncio.gather(*init_tasks)
        for uuid, agent in self._agents.items():
            self._user_chat_topics[uuid] = f"exps/{self.exp_id}/agents/{uuid}/user-chat"
            self._user_survey_topics[uuid] = f"exps/{self.exp_id}/agents/{uuid}/user-survey"

        # save profile
        if self._enable_avro:
            self._avro_path.mkdir(parents=True, exist_ok=True)
            # profile
            filename = self._avro_file["profile"]
            with open(filename, "wb") as f:
                profiles = []
                for agent in self._agents.values():
                    profile = await agent.memory._profile.export()
                    profile = profile[0]
                    profile['id'] = str(agent._uuid)
                    profiles.append(profile)
                fastavro.writer(f, PROFILE_SCHEMA, profiles)

            # dialog
            filename = self._avro_file["dialog"]
            with open(filename, "wb") as f:
                dialogs = []
                fastavro.writer(f, DIALOG_SCHEMA, dialogs)

            # status
            filename = self._avro_file["status"]
            with open(filename, "wb") as f:
                statuses = []
                fastavro.writer(f, STATUS_SCHEMA, statuses)

            # survey
            filename = self._avro_file["survey"]
            with open(filename, "wb") as f:
                surveys = []
                fastavro.writer(f, SURVEY_SCHEMA, surveys)


    async def gather(self, content: str):
        """收集智能体的特定信息"""
        gather_tasks = []
        for group in self._groups.values():
            gather_tasks.append(group.gather.remote(content))
        return await asyncio.gather(*gather_tasks)

    async def update(self, target_agent_id: str, target_key: str, content: Any):
        """更新指定智能体的记忆"""
        group = self._agent_uuid2group[target_agent_id]
        await group.update.remote(target_agent_id, target_key, content)

    def default_memory_config_institution(self):
        """默认的Memory配置函数"""
        EXTRA_ATTRIBUTES = {
            "type": (int, random.choice([economyv2.ORG_TYPE_BANK, economyv2.ORG_TYPE_GOVERNMENT, economyv2.ORG_TYPE_FIRM, economyv2.ORG_TYPE_NBS, economyv2.ORG_TYPE_UNSPECIFIED])),
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
    
    async def send_survey(self, survey: Survey, agent_uuids: Optional[List[uuid.UUID]] = None):
        """发送问卷"""
        survey = survey.to_dict()
        if agent_uuids is None:
            agent_uuids = self._agent_uuids
        payload = {
            "from": "none",
            "survey_id": survey["id"],
            "timestamp": int(datetime.now().timestamp() * 1000),
            "data": survey,
        }
        for uuid in agent_uuids:
            topic = self._user_survey_topics[uuid]
            await self._messager.send_message(topic, payload)

    async def send_interview_message(self, content: str, agent_uuids: Union[uuid.UUID, List[uuid.UUID]]):
        """发送面试消息"""
        payload = {
            "from": "none",
            "content": content,
            "timestamp": int(datetime.now().timestamp() * 1000),
        }
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

    async def run(
        self,
        day: int = 1,
    ):
        """运行模拟器

        Args:
            day: 运行天数,默认为1天
        """
        try:
            # 获取开始时间
            tasks = []
            for group in self._groups.values():
                tasks.append(group.run.remote(day))

            await asyncio.gather(*tasks)

        except Exception as e:
            logger.error(f"模拟器运行错误: {str(e)}")
            raise
