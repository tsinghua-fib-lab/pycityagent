from typing import Any
from .trip import TripAction
from .shop import ShopAction
from .converse import ConverseAction
from .controled import ControledAction
from .idle import IdleAction

class ActionController:
    """
    Agent行为控制器: 与AppHub(simulator)对接
    Agent Controller: Connect with AppHub and Simulator
    Note: Actions are predefined. By now, user defined actions are not supported
    """
    def __init__(self, agent, config=None) -> None:
        self._agent = agent
        self._trip = TripAction(agent)
        self._shop = ShopAction(agent)
        self._converse = ConverseAction(agent)
        self._control = ControledAction(agent)
        self._idle = IdleAction(agent)
        self._config = config

    async def Run(self):
        # TODO: 后期补充相关扩展接口，应该根据state-action关联模块进行（为了方便用户定义更加丰富的状态）
        if self._agent.state == 'idle':
            await self._idle()
        elif self._agent.state == 'trip':
            await self._trip()
        elif self._agent.state == 'conve':
            await self._converse()
        elif self._agent.state == 'shop':
            await self._shop()
        elif self._agent.state == 'controled':
            await self._control()

    @property
    def TripAction(self):
        return self._trip
    
    @property
    def ShopAction(self):
        return self._shop
    
    @property
    def ConveAction(self):
        return self._converse
    
    @property
    def ControlAction(self):
        return self._controls