from abc import ABC, abstractclassmethod
from typing import Any

class Action:
    def __init__(self, agent) -> None:
        '''默认初始化'''
        self._agent = agent

    @abstractclassmethod
    async def Forward(self):
        '''接口函数'''

    async def __call__(self) -> Any:
        await self.Forward()