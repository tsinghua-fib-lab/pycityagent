import time
from .action import Action
from pycitysim.apphub import AgentMessage

class TripAction(Action):
    '''Trip行为控制器'''
    def __init__(self, agent) -> None:
        super().__init__(agent)

    async def Forward(self):
        now = self._agent.Scheduler.now
        if now.is_set:
            '''之前已经将schedule同步至模拟器了'''
            if self._agent.Hub != None:
                self._agent.Hub.Update(streetview=self._agent.Brain.Sence.sence_buffer['streetview'])
        else:
            '''同步schedule至模拟器'''
            self._agent.Scheduler.now.is_set = True
            departure_time = now.time
            mode = now.mode
            aoi_id = now.target_id_aoi
            poi_id = now.target_id_poi
            end = {'aoi_position': {'aoi_id': aoi_id, 'poi_id': poi_id}}
            activity = now.description
            trips = [{'mode': mode, 'end': end, 'departure_time': departure_time, 'activity': activity}]
            set_schedule = [{'trips': trips, 'loop_count': 1, 'departure_time': departure_time}]

            # * 与模拟器对接
            req = {'person_id': self._agent._id, 'schedules': set_schedule}
            await self._agent._client.person_service.SetSchedule(req)

            # * 与AppHub对接
            if self._agent.Hub != None:
                messages = [AgentMessage(self._agent.Hub._agent_id, int(time.time()*1000), f'已到达出发时间, {activity}', None, None)]
                self._agent.Hub.Update(messages)

    