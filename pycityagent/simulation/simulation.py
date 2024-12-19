import asyncio
import json
import logging
import uuid
from datetime import datetime
import random
from typing import Dict, List, Optional, Callable, Union
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
        self._agents: Dict[str, Agent] = {}
        self._groups: Dict[str, AgentGroup] = {}
        self._interview_manager = InterviewManager()
        self._interview_lock = asyncio.Lock()
        self._start_time = datetime.now()
        self._agent_run_times: Dict[str, datetime] = {}  # 记录每个智能体的运行开始时间
        self._ui: Optional[InterviewUI] = None
        self._loop = asyncio.get_event_loop()
        self._blocked_agents: List[str] = []  # 新增：持续阻塞的智能体列表
        self._survey_manager = SurveyManager()
        self._agentid2group: Dict[str, AgentGroup] = {}
        self._agent_ids: List[str] = []

    async def init_agents(
        self,
        agent_count: Union[int, list[int]],
        group_size: int = 1000,
        memory_config_func: Union[Callable, list[Callable]] = None,
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

                self._agents[agent_name] = agent

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
                group_name = f"{self.agent_prefix}_{i}_group_{k}"
                group = AgentGroup.remote(agents, self.config, self.exp_id)
                self._groups[group_name] = group

            class_init_index += agent_count_i  # 更新类初始索引

        init_tasks = []
        for group in self._groups.values():
            init_tasks.append(group.init_agents.remote())
        await asyncio.gather(*init_tasks)

        for group in self._groups.values():
            agent_ids = await group.gather.remote("id")
            for agent_id in agent_ids:
                self._agent_ids.append(agent_id)
                self._agentid2group[agent_id] = group

    async def gather(self, content: str):
        """收集所有智能体的ID"""
        gather_tasks = []
        for group in self._groups.values():
            gather_tasks.append(group.gather.remote(content))
        return await asyncio.gather(*gather_tasks)

    async def update(self, target_agent_id: str, target_key: str, content: any):
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

    def get_agent_runtime(self, agent_name: str) -> str:
        """获取智能体运行时间"""
        if agent_name not in self._agent_run_times:
            return "-"
        delta = datetime.now() - self._agent_run_times[agent_name]
        hours = delta.seconds // 3600
        minutes = (delta.seconds % 3600) // 60
        seconds = delta.seconds % 60
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"

    def get_total_runtime(self) -> str:
        """获取总运行时间"""
        delta = datetime.now() - self._start_time
        hours = delta.seconds // 3600
        minutes = (delta.seconds % 3600) // 60
        seconds = delta.seconds % 60
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"

    def export_chat_history(self, agent_name: str | None) -> str:
        """导出对话历史

        Args:
            agent_name: 可选的智能体名称，如果提供则只导出该智能体的对话

        Returns:
            str: JSON格式的对话历史
        """
        history = (
            self._interview_manager.get_agent_history(agent_name)
            if agent_name
            else self._interview_manager.get_recent_history(limit=1000)
        )

        # 转换为易读格式
        formatted_history = []
        for record in history:
            formatted_history.append(
                {
                    "timestamp": record.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
                    "agent": record.agent_name,
                    "question": record.question,
                    "response": record.response,
                    "blocking": record.blocking,
                }
            )

        return json.dumps(formatted_history, ensure_ascii=False, indent=2)

    def toggle_agent_block(self, agent_name: str, blocking: bool) -> str:
        """切换智能体的阻塞状态

        Args:
            agent_name: 能体名称
            blocking: True表示阻塞，False表示取消阻塞

        Returns:
            str: 状态变更消息
        """
        if agent_name not in self._agents:
            return f"找不到智能体 {agent_name}"

        if blocking and agent_name not in self._blocked_agents:
            self._blocked_agents.append(agent_name)
            self._agents[agent_name]._blocked = True
            return f"已阻塞智能体 {agent_name}"
        elif not blocking and agent_name in self._blocked_agents:
            self._blocked_agents.remove(agent_name)
            self._agents[agent_name]._blocked = False
            return f"已取消阻塞智能体 {agent_name}"

        return f"智能体 {agent_name} 状态未变"

    async def interview_agent(self, agent_name: str, question: str) -> str:
        """采访指定智能体"""
        agent = self._agents.get(agent_name)
        if not agent:
            return "找不到指定的智能体"

        try:
            response = await agent.generate_response(question)
            # 记录采访历史
            self._interview_manager.add_record(
                agent_name,
                question,
                response,
                blocking=(agent_name in self._blocked_agents),
            )
            return response

        except Exception as e:
            logger.error(f"采访过程出错: {str(e)}")
            return f"采访过程出现错误: {str(e)}"

    async def submit_survey(self, agent_name: str, survey_id: str) -> str:
        """向智能体提交问卷

        Args:
            agent_name: 智能体名称
            survey_id: 问卷ID

        Returns:
            str: 处理结果
        """
        agent = self._agents.get(agent_name)
        if not agent:
            return "找不到指定的智能体"

        survey = self._survey_manager.get_survey(survey_id)
        if not survey:
            return "找不到指定的问卷"

        try:
            # 建问卷提示
            prompt = f"""请以第一人称回答以下调查问卷:

问卷标题: {survey.title}
问卷说明: {survey.description}

"""
            for i, question in enumerate(survey.questions):
                prompt += f"\n问题{i+1}. {question.content}"
                if question.type in (
                    QuestionType.SINGLE_CHOICE,
                    QuestionType.MULTIPLE_CHOICE,
                ):
                    prompt += "\n选项: " + ", ".join(question.options)
                elif question.type == QuestionType.RATING:
                    prompt += (
                        f"\n(请给出{question.min_rating}-{question.max_rating}的评分)"
                    )
                elif question.type == QuestionType.LIKERT:
                    prompt += "\n(1-强烈不同意, 2-不同意, 3-中立, 4-同意, 5-强烈同意)"

            # 生成回答
            response = await agent.generate_response(prompt)

            # 存储原始回答
            self._survey_manager.add_response(
                survey_id, agent_name, {"raw_response": response, "parsed": False}
            )

            return response

        except Exception as e:
            logger.error(f"问卷处理出错: {str(e)}")
            return f"问卷处理出现错误: {str(e)}"

    def create_survey(self, **survey_data: dict) -> None:
        """创建新问卷

        Args:
            survey_data: 问卷数据，包含 title, description, questions

        Returns:
            更新后的问卷列表
        """
        self._survey_manager.create_survey(**survey_data)  # type:ignore

    def get_surveys(self) -> list:
        """获取所有问卷"""
        return self._survey_manager.get_all_surveys()

    def get_survey_questions(self, survey_id: str) -> dict | None:
        """获取指定问卷的问题列表

        Args:
            survey_id: 问卷ID

        Returns:
            问卷数据，包含 title, description, questions
        """
        for _, survey in self._survey_manager._surveys.items():
            survey_dict = survey.to_dict()
            if survey_dict["id"] == survey_id:
                return survey_dict
        return None

    async def init_ui(
        self,
        server_name: str = "127.0.0.1",
        server_port: int = 7860,
    ):
        """初始化UI"""
        self._interview_lock = asyncio.Lock()
        # 初始化GradioUI
        self._ui = InterviewUI(self)
        interface = self._ui.create_interface()
        interface.queue().launch(
            server_name=server_name,
            server_port=server_port,
            prevent_thread_lock=True,
            quiet=True,
        )
        logger.info(f"Gradio Frontend is running on http://{server_name}:{server_port}")

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
