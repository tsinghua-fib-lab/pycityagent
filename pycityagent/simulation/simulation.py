import asyncio
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional

from ..agent import Agent
from ..environment import Simulator
from .interview import InterviewManager
from .survey import QuestionType, Survey, SurveyManager
from .ui import InterviewUI

logger = logging.getLogger(__name__)


class AgentSimulation:
    """城市智能体模拟器"""

    def __init__(self, simulator: Optional[Simulator] = None):
        self.simulator = simulator
        self._agents: Dict[str, Agent] = {}
        self._interview_manager = InterviewManager()
        self._interview_lock = asyncio.Lock()
        self._start_time = datetime.now()
        self._agent_run_times: Dict[str, datetime] = {}  # 记录每个智能体的运行开始时间
        self._ui: Optional[InterviewUI] = None
        self._loop = asyncio.get_event_loop()
        self._blocked_agents: List[str] = []  # 新增：持续阻塞的智能体列表
        self._survey_manager = SurveyManager()

    def add_agent(self, agent: Agent) -> None:
        """添加智能体到模拟器"""
        if agent._name in self._agents:
            raise ValueError(f"智能体 {agent._name} 已存在")
        self._agents[agent._name] = agent
        self._agent_run_times[agent._name] = datetime.now()
        logger.info(f"添加智能体: {agent._name}")

    def remove_agent(self, agent_name: str) -> None:
        """从模拟器中移除智能体"""
        if agent_name in self._agents:
            del self._agents[agent_name]
            del self._agent_run_times[agent_name]
            logger.info(f"移除智能体: {agent_name}")

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
            return f"已阻塞智能体 {agent_name}"
        elif not blocking and agent_name in self._blocked_agents:
            self._blocked_agents.remove(agent_name)
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

    async def run(
        self,
        steps: int = -1,
        interval: float = 1.0,
        start_ui: bool = True,
        server_name: str = "127.0.0.1",
        server_port: int = 7860,
    ):
        """运行模拟器

        Args:
            steps: 运行步数,默认为-1表示无限运行
            interval: 智能体forward间隔时间,单位为秒,默认1秒
            start_ui: 是否启动UI,默认为True
            server_name: UI服务器地址,默认为"127.0.0.1"
            server_port: UI服务器端口,默认为7860
        """
        try:
            self._interview_lock = asyncio.Lock()
            # 初始化UI
            if start_ui:
                self._ui = InterviewUI(self)
                interface = self._ui.create_interface()
                interface.queue().launch(
                    server_name=server_name,
                    server_port=server_port,
                    prevent_thread_lock=True,
                    quiet=True,
                )
                print(
                    f"Gradio Frontend is running on http://{server_name}:{server_port}"
                )

            # 运行所有agents
            tasks = []
            for agent in self._agents.values():
                tasks.append(self._run_agent(agent, steps, interval))

            await asyncio.gather(*tasks)

        except Exception as e:
            logger.error(f"模拟器运行错误: {str(e)}")
            raise

    async def _run_agent(self, agent: Agent, steps: int = -1, interval: float = 1.0):
        """运行单个agent的包装器

        Args:
            agent: 要运行的能体
            steps: 运行步数,默认为-1表示无限运行
            interval: 智能体forward间隔时间,单位为秒
        """
        step_count = 0
        while steps == -1 or step_count < steps:
            try:
                if agent._name in self._blocked_agents:
                    await asyncio.sleep(interval)
                    continue

                await agent.forward()
                await asyncio.sleep(interval)  # 控制运行频率
                step_count += 1

            except Exception as e:
                logger.error(f"智能体 {agent._name} 运行错误: {str(e)}")
                await asyncio.sleep(interval)  # 发生错误时暂停一下

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
