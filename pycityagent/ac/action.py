from abc import ABC, abstractclassmethod
from typing import Callable, Any

class ActionType:
    """
    行动类型枚举 所有行动本质上为数据推送
    Action Type enumeration, all actions are essentially data push

    Types:
    - Sim = 1, 用于表示与模拟器对接的行动
    - Hub = 2, 用于表示与AppHub(前端)对接的行动
    - Comp = 3, 表示综合类型 (可能同时包含与Sim以及Hub的交互)
    """
    Sim = 1
    Hub = 2
    Comp = 3
class Action:
    def __init__(self, agent, type:ActionType, source: str = None, before:Callable[[list], Any] = None) -> None:
        '''
        默认初始化
        
        Args:
        - agent (Agent): the related agent
        - type (ActionType)
        - source (str): 数据来源, 默认为None, 如果为None则会从接收用户传入的数据作为Forward函数参数, 否则从WM.Reason数据缓存中取对应数据作为参数
        - before (function): 数据处理方法, 用于当Reason缓存中的参数与标准格式不符时使用
        '''
        self._agent = agent
        self._type = type
        self._source = source
        self._before = before

    def get_source(self):
        """
        获取source数据
        """
        if self._source != None:
            source = self._agent.Brain.Memory.Working.Reason[self._source]
            if self._before != None:
                source = self._before(source)
            return source
        else:
            return None

    @abstractclassmethod
    async def Forward(self):
        '''接口函数'''

class SimAction(Action):
    def __init__(self, agent, source: str = None, before: Callable[[list], Any] = None) -> None:
        super().__init__(agent, ActionType.Sim, source, before)

class HubAction(Action):
    def __init__(self, agent, source: str = None, before: Callable[[list], Any] = None) -> None:
        super().__init__(agent, ActionType.Hub, source, before)