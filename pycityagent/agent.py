"""智能体模板类及其定义"""

from abc import abstractmethod
from enum import Enum
from .llm import LLM
from typing import List, Optional

from .environment import Simulator
from .llm import *
from .memory import Memory
from .workflow import Workflow

class AgentType(Enum):
    """
    Agent类型

    - Citizen, Citizen type agent
    - Institution, Orgnization or institution type agent
    """
    Citizen = "Citizen"
    Institution = "Inistitution"


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

    def add_workflow(self, workflow: Workflow) -> None:
        if self._memory is None:
            raise ValueError("Memory is not set yet.")
        workflow.bind_memory(self._memory)
        workflow.bind_simulator(self._simulator)
        workflow.bind_llm(self._llm)
        self.workflows.append(workflow)

    async def start_all_workflows(self) -> None:
        for workflow in self.workflows:
            await workflow.start()

    def stop_all_workflows(self) -> None:
        for workflow in self.workflows:
            workflow.stop()
    
    @property
    async def LLM(self):
        """The Agent's Soul(UrbanLLM)"""
        return self._llm
    
class CitizenAgent(Agent):
    """
    CitizenAgent: 城市居民智能体类及其定义
    """
    def __init__(self, name: str, llm_client: LLM, simulator: Simulator, memory: Optional[Memory] = None) -> None:
        super().__init__(name, AgentType.Citizen, llm_client, simulator, memory)

class InistitutionAgent(Agent):
    """
    InistitutionAgent: 机构智能体类及其定义
    """
    def __init__(self, name: str, llm_client: LLM, simulator: Simulator, memory: Optional[Memory] = None) -> None:
        super().__init__(name, AgentType.Institution, llm_client, simulator, memory)

    
