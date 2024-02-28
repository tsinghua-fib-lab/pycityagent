import time
from .action import Action
from pycitysim.apphub import AgentMessage

class ControledAction(Action):
    '''Converse行为控制器'''
    def __init__(self, agent) -> None:
        super().__init__(agent)

    async def Forward(self):
        req = {'person_id': self._agent._id, 'schedules': []}
        await self._agent._client.person_service.SetSchedule(req)
        self._agent.Hub.Update([AgentMessage(self._agent.Hub._agent_id, int(time.time()*1000), '我已理解您的意思，正在修改我的行程', None, None)])