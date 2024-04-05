import time
from typing import Callable, Any

from pycityagent.ac.action import ActionType
from ..action import Action
from pycitysim.apphub import AgentMessage

class ConverseAction(Action):
    '''Converse行为控制器'''
    def __init__(self, agent, sources: list[str] = None, before: Callable[[list], Any] = None) -> None:
        super().__init__(agent, ActionType.Comp, sources, before)

    async def Forward(self):
        target_agent_ids = self._agent.Brain.Memory.Working.Reason['agent_message_handle_resp'][0]
        if len(target_agent_ids) == 0:
            return
        messages = self._agent.Brain.Memory.Working.Reason['agent_message_handle_resp'][1]
        req = {'messages': []}
        if len(target_agent_ids) != len(messages):
            print("Warning: the number of target agent and message are not aligned, only sends matched messages")
        rng = min(len(target_agent_ids), len(messages))
        for i in range(rng):
            dic = {}
            dic['from'] = self._agent._id
            dic['to'] = target_agent_ids[i]
            dic['message'] = messages[i]
            req['messages'].append(dic)
        # * 发送至模拟器
        await self._agent._client.social_service.Send(req=req)

        # * 发送至AppHub
        if self._agent.Hub != None and messages[0] != 'End':
            # * 将信息中的第一条不同至pop
            self._agent.Hub.Update(pop=messages[0])