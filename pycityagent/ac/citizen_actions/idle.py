import time
from typing import Callable, Any

from pycityagent.ac.action import ActionType
from ..action import Action
from pycitysim.apphub import AgentMessage

class IdleAction(Action):
    '''idle行为控制器'''
    def __init__(self, agent, sources: list[str] = None, before: Callable[[list], Any] = None) -> None:
        super().__init__(agent, ActionType.Comp, sources, before)

    async def Forward(self):
        if len(self._agent.base['schedules']) > 0:
            req = {'person_id': self._agent._id, 'schedules': []}
            await self._agent._client.person_service.SetSchedule(req)
        if self._agent.Hub != None:
            self._agent.Hub.Update()

    