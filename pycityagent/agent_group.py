"""GroupAgent群体智能体"""

from typing import Union, Optional
from pycityagent.urbanllm import UrbanLLM
from .urbanllm import UrbanLLM
from .agent import Agent, AgentType
from .image.image import Image
from .ac.hub_actions import PositionUpdate
from .agent_func import FuncAgent
from .utils import *

class GroupAgent(Agent):
    """
    GroupAgent
    群体智能体
    """

    def __init__(
            self, 
            name: str, 
            soul: UrbanLLM = None, 
            simulator=None
        ) -> None:
        super().__init__(name, simulator.config['simulator']['server'], AgentType.Group, soul, simulator)
        self.agents:list[FuncAgent] = []
        """
        Agent列表
        """

    def add_agents(self, agents:Optional[list[FuncAgent]]=None, ids: Optional[Union[int, list[int], tuple]]=None, number:Optional[int]=1):
        """
        添加一个或多个智能体

        Args:
        - agents: FuncAgent列表
        - ids: 智能体id
            - int: 添加单个智能体
            - list[int]: 添加多个智能体
            - tuple(int, int): 根据范围确定添加智能体个数
        - number: 智能体个数
            - 与int类型ids参数配合使用
        """
        if agents != None:
            self.agents = agents
        elif isinstance(ids, int):
            for i in range(number):
                agent = FuncAgent(
                    f"{self._name}_{ids+i}",
                    ids+i,
                    self._simulator.config['simulator']['server'],
                    simulator=self._simulator
                )
                self.agents.append(agent)
        elif isinstance(ids, list):
            for id in ids:
                agent = FuncAgent(
                    f"{self._name}_{id}",
                    id,
                    self._simulator.config['simulator']['server'],
                    simulator=self._simulator
                )
                self.agents.append(agent)
        elif isinstance(ids, tuple):
            if len(ids) == 2 and ids[0] <= ids[0]:
                for i in range(ids[0], ids[1]+1):
                    agent = FuncAgent(
                        f"{self._name}_{i}",
                        i,
                        self._simulator.config['simulator']['server'],
                        simulator=self._simulator
                    )
                    self.agents.append(agent)
            else:
                raise Exception(f"Error: wrong id tuple: {ids}")
        else:
            raise Exception("Wrong parameter")
        
    def ConnectToHub(self, config: dict):
        for agent in self.agents:
            agent.ConnectToHub(config)

    def Bind(self):
        for agent in self.agents:
            agent.Bind()