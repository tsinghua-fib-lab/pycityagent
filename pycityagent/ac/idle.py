import time
from .action import Action
from pycitysim.apphub import AgentMessage

class IdleAction(Action):
    '''idle行为控制器'''
    def __init__(self, agent) -> None:
        super().__init__(agent)

    async def Forward(self):
        if len(self._agent.base['schedules']) > 0:
            req = {'person_id': self._agent._id, 'schedules': []}
            await self._agent._client.person_service.SetSchedule(req)
        if self._agent.Hub != None:
            self._agent.Hub.Update()

    