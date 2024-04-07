import time
from typing import Callable, Optional, Any
from .action import SimAction
from ..brain.scheduler import TripSchedule

class SetSchedule(SimAction):
    """
    用于将agent的行程信息同步至模拟器 —— 仅对citizen类型agent适用
    Synchronize agent's schedule to simulator —— only avalable for citizen type of agent
    """
    def __init__(self, agent, sources: list[str] = None, before: Callable[[list], Any] = None) -> None:
        super().__init__(agent, sources, before)

    async def Forward(self, schedule: Optional[TripSchedule] = None):
        """
        如果当前行程已经同步至模拟器: 跳过同步, 否则同步至模拟器
        If current schedule has been synchronized to simulator: skip, else sync
        """
        if not schedule == None:
            if not schedule.is_set:
                '''同步schedule至模拟器'''
                self._agent.Scheduler.now.is_set = True
                departure_time = schedule.time
                mode = schedule.mode
                aoi_id = schedule.target_id_aoi
                poi_id = schedule.target_id_poi
                end = {'aoi_position': {'aoi_id': aoi_id, 'poi_id': poi_id}}
                activity = schedule.description
                trips = [{'mode': mode, 'end': end, 'departure_time': departure_time, 'activity': activity}]
                set_schedule = [{'trips': trips, 'loop_count': 1, 'departure_time': departure_time}]

                # * 与模拟器对接
                req = {'person_id': self._agent._id, 'schedules': set_schedule}
                await self._agent._client.person_service.SetSchedule(req)
        elif self._source != None:
            schedule = self.get_source()
            if schedule != None and not schedule.is_set:
                '''同步schedule至模拟器'''
                self._agent.Scheduler.now.is_set = True
                departure_time = schedule.time
                mode = schedule.mode
                aoi_id = schedule.target_id_aoi
                poi_id = schedule.target_id_poi
                end = {'aoi_position': {'aoi_id': aoi_id, 'poi_id': poi_id}}
                activity = schedule.description
                trips = [{'mode': mode, 'end': end, 'departure_time': departure_time, 'activity': activity}]
                set_schedule = [{'trips': trips, 'loop_count': 1, 'departure_time': departure_time}]

                # * 与模拟器对接
                req = {'person_id': self._agent._id, 'schedules': set_schedule}
                await self._agent._client.person_service.SetSchedule(req)


class SendAgentMessage(SimAction):
    """
    发送信息给其他agent
    Send messages to other agents
    """
    def __init__(self, agent, sources: list[str] = None, before: Callable[[list], Any] = None) -> None:
        super().__init__(agent, sources, before)

    async def Forward(self, messages: Optional[dict] = None):
        if not messages == None and len(messages) > 0:
            req = {'messages': []}
            for message in messages:
                from_id = self._agent._id
                to_id = message['id']
                mes = message['message']
                req['messages'].append({'from': from_id, 'to': to_id, 'message': mes})
            await self._agent._client.social_service.Send(req)
        elif self._source != None:
            messages = self.get_source()
            if not messages == None and len(messages) > 0:
                req = {'messages': []}
                for message in messages:
                    from_id = self._agent._id
                    to_id = message['id']
                    mes = message['message']
                    req['messages'].append({'from': from_id, 'to': to_id, 'message': mes})
                await self._agent._client.social_service.Send(req)
