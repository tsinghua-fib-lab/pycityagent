"""智能体模板类及其定义"""

from abc import ABC, abstractmethod
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional

from .economy import EconomyClient
from .environment import Simulator
from .llm import LLM
from .memory import Memory


class AgentType(Enum):
    """
    Agent类型

    - Citizen, Citizen type agent
    - Institution, Orgnization or institution type agent
    """

    Unspecified = "Unspecified"
    Citizen = "Citizen"
    Institution = "Institution"


class Agent(ABC):
    """
    Agent base class
    """

    def __init__(
        self,
        name: str,
        type: AgentType = AgentType.Unspecified,
        llm_client: Optional[LLM] = None,
        economy_client: Optional[EconomyClient] = None,
        simulator: Optional[Simulator] = None,
        memory: Optional[Memory] = None,
    ) -> None:
        """
        Initialize the Agent.

        Args:
            name (str): The name of the agent.
            type (AgentType): The type of the agent. Defaults to `AgentType.Unspecified`
            llm_client (LLM): The language model client. Defaults to None.
            economy_client (EconomyClient): The `EconomySim` client. Defaults to None.
            simulator (Simulator, optional): The simulator object. Defaults to None.
            memory (Memory, optional): The memory of the agent. Defaults to None.
        """
        self._name = name
        self._type = type
        self._llm_client = llm_client
        self._economy_client = economy_client
        self._simulator = simulator
        self._memory = memory
        self._has_bound_to_simulator = False
        self._interview_history: List[Dict] = []  # 存储采访历史

    def set_memory(self, memory: Memory):
        """
        Set the memory of the agent.
        """
        self._memory = memory

    def set_simulator(self, simulator: Simulator):
        """
        Set the simulator of the agent.
        """
        self._simulator = simulator

    def set_economy_client(self, economy_client: EconomyClient):
        """
        Set the economy_client of the agent.
        """
        self._economy_client = economy_client

    @property
    def LLM(self):
        """The Agent's LLM"""
        if self._llm_client is None:
            raise RuntimeError(
                f"LLM access before assignment, please `set_llm_client` first!"
            )
        return self._llm_client

    @property
    def economy_client(self):
        """The Agent's EconomyClient"""
        if self._economy_client is None:
            raise RuntimeError(
                f"EconomyClient access before assignment, please `set_economy_client` first!"
            )
        return self._economy_client

    @property
    def memory(self):
        """The Agent's Memory"""
        if self._memory is None:
            raise RuntimeError(
                f"Memory access before assignment, please `set_memory` first!"
            )
        return self._memory

    @property
    def simulator(self):
        """The Simulator"""
        if self._simulator is None:
            raise RuntimeError(
                f"Simulator access before assignment, please `set_simulator` first!"
            )
        return self._simulator

    async def generate_response(self, question: str) -> str:
        """生成回答

        基于智能体的记忆和当前状态，生成对问题的回答。

        Args:
            question: 需要回答的问题

        Returns:
            str: 智能体的回答
        """
        dialog = []

        # 添加系统提示
        system_prompt = f"请以第一人称的方式回答问题,保持回答简洁明了。"
        dialog.append({"role": "system", "content": system_prompt})

        # 添加记忆上下文
        if self._memory:
            relevant_memories = await self._memory.search(question)
            if relevant_memories:
                dialog.append(
                    {
                        "role": "system",
                        "content": f"基于以下记忆回答问题:\n{relevant_memories}",
                    }
                )

        # 添加用户问题
        dialog.append({"role": "user", "content": question})

        # 使用LLM生成回答
        if not self._llm_client:
            return "抱歉，我现在无法回答问题。"

        response = await self._llm_client.atext_request(dialog)  # type:ignore

        # 记录采访历史
        self._interview_history.append(
            {
                "timestamp": datetime.now().isoformat(),
                "question": question,
                "response": response,
            }
        )

        return response  # type:ignore

    def get_interview_history(self) -> List[Dict]:
        """获取采访历史记录"""
        return self._interview_history

    @abstractmethod
    async def forward(self) -> None:
        """智能体行为逻辑"""
        raise NotImplementedError


class CitizenAgent(Agent):
    """
    CitizenAgent: 城市居民智能体类及其定义
    """

    def __init__(
        self,
        name: str,
        llm_client: Optional[LLM] = None,
        simulator: Optional[Simulator] = None,
        memory: Optional[Memory] = None,
    ) -> None:
        super().__init__(
            name,
            AgentType.Citizen,
            llm_client,
            None,
            simulator,
            memory,
        )


class InstitutionAgent(Agent):
    """
    InstitutionAgent: 机构智能体类及其定义
    """

    def __init__(
        self,
        name: str,
        llm_client: Optional[LLM] = None,
        simulator: Optional[Simulator] = None,
        memory: Optional[Memory] = None,
    ) -> None:
        super().__init__(
            name,
            AgentType.Institution,
            llm_client,
            None,
            simulator,
            memory,
        )
