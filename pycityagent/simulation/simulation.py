import asyncio
import json
import logging
import uuid
from datetime import datetime
import random
from typing import Dict, List, Optional, Callable, Union,Any
from mosstool.map._map_util.const import AOI_START_ID

from pycityagent.memory.memory import Memory

from ..agent import Agent
from .interview import InterviewManager
from .survey import QuestionType, SurveyManager
from .ui import InterviewUI
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
        self._agentid2group: Dict[uuid.UUID, AgentGroup] = {}
        self._agent_ids: List[uuid.UUID] = []

        self._loop = asyncio.get_event_loop()
        self._interview_manager = InterviewManager()
        self._survey_manager = SurveyManager()

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
            memory_config_func = [self.default_memory_config_func]
        elif not isinstance(memory_config_func, list):
            memory_config_func = [memory_config_func]

        if len(memory_config_func) != len(agent_count):
            logging.warning(
                "memory_config_func和agent_count的长度不一致，使用默认的memory_config_func"
            )
            memory_config_func = [self.default_memory_config_func] * len(agent_count)

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
                    config=extra_attributes, profile=profile.copy(), base=base.copy()
                )

                # 创建智能体时传入Memory配置
                agent = agent_class(
                    name=agent_name,
                    memory=memory,
                )

                self._agents[agent._uuid] = agent
                self._agent_ids.append(agent._uuid)

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
                group = AgentGroup.remote(agents, self.config, self.exp_id)
                self._groups[group_name] = group
                for agent in agents:
                    self._agentid2group[agent._uuid] = group

            class_init_index += agent_count_i  # 更新类初始索引

        init_tasks = []
        for group in self._groups.values():
            init_tasks.append(group.init_agents.remote())
        await asyncio.gather(*init_tasks)

    async def gather(self, content: str):
        """收集智能体的特定信息"""
        gather_tasks = []
        for group in self._groups.values():
            gather_tasks.append(group.gather.remote(content))
        return await asyncio.gather(*gather_tasks)

    async def update(self, target_agent_id: str, target_key: str, content: Any):
        """更新指定智能体的记忆"""
        group = self._agentid2group[target_agent_id]
        await group.update.remote(target_agent_id, target_key, content)

    def default_memory_config_func(self):
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
            "income": random.randint(1000, 10000),
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
