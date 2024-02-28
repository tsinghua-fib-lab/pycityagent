from abc import ABC, abstractmethod
from typing import Optional
from .scheduler import Scheduler
from .sence import Sence
from .memory import MemoryController

class Brain:
    """
    大脑模块
    Brain Module
    """
    def __init__(self, agent) -> None:
        self._agent = agent
        self._simulator = agent._simulator
        self._sence = Sence(agent)
        """
        感知模块
        Sence module
        """
        self._memory = MemoryController(agent)
        """
        记忆模块
        Memory module
        """

    async def Run(self):
        """
        大脑主工作流
        The main workflow of Brain
        """
        await self._sence.Sence()
        await self._memory.Forward()

    @property
    def Agent(self):
        return self._agent
    
    @property
    def Sence(self):
        return self._sence
    
    @property
    def Memory(self):
        return self._memory
    
    @property
    def Simulator(self):
        return self._simulator
    
    @property
    def Hub(self):
        return self._hub