"""智能体模板类及其定义"""

from abc import abstractmethod
from llm import *
from typing import List, Optional
from .environment import Simulator
from .memory import Memory
from .workflow import Workflow

class AgentType:
    """
    Agent类型

    - Citizen = 1, Citizen type agent
    - Institution = 2, Orgnization or institution type agent
    """
    Citizen = 1
    Institution = 2

class Agent:
    """
    Agent base class
    """
    def __init__(
            self, 
            name: str, 
            type: AgentType,
            llm_client: LLM, 
            simulator: Simulator,
            memory: Optional[Memory] = None,
        ) -> None:
        """
        Initialize the Agent.

        Args:
            name (str): The name of the agent.
            type (AgentType): The type of the agent.
            llm_client (LLM): The language model client.
            simulator (Simulator): The simulator object.
            memory (Memory, optional): The memory of the agent. Defaults to None.
        """
        self._name = name
        self._type = type
        self._llm = llm_client
        self._simulator = simulator
        self._memory = memory
        self.workflows: List[Workflow] = []

    async def set_memory(self, memory: Memory):
        """
        Set the memory of the agent.
        """
        self._memory = memory

    @abstractmethod
    async def step(self):
        """Unified execution entry"""
        raise NotImplementedError
    
    @property
    async def LLM(self):
        """The Agent's Soul(UrbanLLM)"""
        return self._llm