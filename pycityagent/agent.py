"""智能体模板类及其定义"""

from abc import abstractmethod
from enum import Enum
from typing import List, Optional

from .environment import Simulator
from .llm import *
from .llm import LLM
from .memory import Memory

# from .workflow import Workflow


class AgentType(Enum):
    """
    Agent类型

    - Citizen, Citizen type agent
    - Institution, Orgnization or institution type agent
    """

    Unspecified = "Unspecified"
    Citizen = "Citizen"
    Institution = "Inistitution"


class Agent:
    """
    Agent base class
    """

    def __init__(
        self,
        name: str,
        type: AgentType = AgentType.Unspecified,
        llm_client: Optional[LLM] = None,
        simulator: Optional[Simulator] = None,
        memory: Optional[Memory] = None,
    ) -> None:
        """
        Initialize the Agent.

        Args:
            name (str): The name of the agent.
            type (AgentType): The type of the agent. Defaults to `AgentType.Unspecified`
            llm_client (LLM): The language model client. Defaults to None.
            simulator (Simulator, optional): The simulator object. Defaults to None.
            memory (Memory, optional): The memory of the agent. Defaults to None.
        """
        self.name = name
        self._type = type
        self._llm = llm_client
        self._simulator = simulator
        self._memory = memory

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

    @property
    def LLM(self):
        """The Agent's LLM"""
        if self._llm is None:
            raise RuntimeError(
                f"LLM access before assignment, please `set_llm_client` first!"
            )
        return self._llm

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

    async def forward(self):
        """
        Defines how the blocks are executed. To be implemented by subclasses.
        """
        raise NotImplementedError("Subclasses should implement this method")


class CitizenAgent(Agent):
    """
    CitizenAgent: 城市居民智能体类及其定义
    """

    def __init__(
        self,
        name: str,
        llm_client: LLM,
        simulator: Optional[Simulator] = None,
        memory: Optional[Memory] = None,
    ) -> None:
        super().__init__(
            name,
            AgentType.Citizen,
            llm_client,
            simulator,
            memory,
        )


class InistitutionAgent(Agent):
    """
    InistitutionAgent: 机构智能体类及其定义
    """

    def __init__(
        self,
        name: str,
        llm_client: LLM,
        simulator: Optional[Simulator] = None,
        memory: Optional[Memory] = None,
    ) -> None:
        super().__init__(
            name,
            AgentType.Institution,
            llm_client,
            simulator,
            memory,
        )
