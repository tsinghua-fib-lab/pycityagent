"""环境相关的Interaction定义"""

from enum import Enum
from typing import Callable, Optional, Any
from abc import ABC, abstractmethod
from typing import Callable, Any


class ActionType(Enum):
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
    """
    - Action
    """

    def __init__(
        self,
        agent,
        type: ActionType,
        source: Optional[str] = None,
        before: Optional[Callable[[list], Any]] = None,
    ) -> None:
        """
        默认初始化

        Args:
        - agent (Agent): the related agent
        - type (ActionType)
        - source (str): 数据来源, 默认为None, 如果为None则会从接收用户传入的数据作为Forward函数参数, 否则从WM.Reason数据缓存中取对应数据作为参数
        - before (function): 数据处理方法, 用于当Reason缓存中的参数与标准格式不符时使用
        """
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

    @abstractmethod
    async def Forward(self):
        """接口函数"""


class SimAction(Action):
    """SimAction: 模拟器关联Action"""

    def __init__(
        self,
        agent,
        source: Optional[str] = None,
        before: Optional[Callable[[list], Any]] = None,
    ) -> None:
        super().__init__(agent, ActionType.Sim, source, before)


class HubAction(Action):
    """HubAction: Apphub关联Action"""

    def __init__(
        self,
        agent,
        source: Optional[str] = None,
        before: Optional[Callable[[list], Any]] = None,
    ) -> None:
        super().__init__(agent, ActionType.Hub, source, before)


class SetSchedule(SimAction):
    """
    用于将agent的行程信息同步至模拟器 —— 仅对citizen类型agent适用
    Synchronize agent's schedule to simulator —— only avalable for citizen type of agent
    """

    def __init__(
        self,
        agent,
        source: Optional[str] = None,
        before: Optional[Callable[[list], Any]] = None,
    ) -> None:
        super().__init__(agent, source, before)

    async def Forward(self, schedule=None):
        """
        如果当前行程已经同步至模拟器: 跳过同步, 否则同步至模拟器
        If current schedule has been synchronized to simulator: skip, else sync
        """
        if not schedule == None:
            if not schedule.is_set:
                """同步schedule至模拟器"""
                self._agent.Scheduler.now.is_set = True
                departure_time = schedule.time
                mode = schedule.mode
                aoi_id = schedule.target_id_aoi
                poi_id = schedule.target_id_poi
                end = {"aoi_position": {"aoi_id": aoi_id, "poi_id": poi_id}}
                activity = schedule.description
                trips = [
                    {
                        "mode": mode,
                        "end": end,
                        "departure_time": departure_time,
                        "activity": activity,
                    }
                ]
                set_schedule = [
                    {"trips": trips, "loop_count": 1, "departure_time": departure_time}
                ]

                # * 与模拟器对接
                req = {"person_id": self._agent._id, "schedules": set_schedule}
                await self._agent._client.person_service.SetSchedule(req)
        elif self._source != None:
            schedule = self.get_source()
            if schedule != None and not schedule.is_set:
                """同步schedule至模拟器"""
                self._agent.Scheduler.now.is_set = True
                departure_time = schedule.time
                mode = schedule.mode
                aoi_id = schedule.target_id_aoi
                poi_id = schedule.target_id_poi
                end = {"aoi_position": {"aoi_id": aoi_id, "poi_id": poi_id}}
                activity = schedule.description
                trips = [
                    {
                        "mode": mode,
                        "end": end,
                        "departure_time": departure_time,
                        "activity": activity,
                    }
                ]
                set_schedule = [
                    {"trips": trips, "loop_count": 1, "departure_time": departure_time}
                ]

                # * 与模拟器对接
                req = {"person_id": self._agent._id, "schedules": set_schedule}
                await self._agent._client.person_service.SetSchedule(req)


class SendAgentMessage(SimAction):
    """
    发送信息给其他agent
    Send messages to other agents
    """

    def __init__(
        self,
        agent,
        source: Optional[str] = None,
        before: Optional[Callable[[list], Any]] = None,
    ) -> None:
        super().__init__(agent, source, before)

    async def Forward(self, messages: Optional[dict] = None):
        if not messages == None and len(messages) > 0:
            req = {"messages": []}
            for message in messages:
                from_id = self._agent._id
                to_id = message["id"]
                mes = message["message"]
                req["messages"].append({"from": from_id, "to": to_id, "message": mes})
            await self._agent._client.social_service.Send(req)
        elif self._source != None:
            messages = self.get_source()
            if not messages == None and len(messages) > 0:
                req = {"messages": []}
                for message in messages:
                    from_id = self._agent._id
                    to_id = message["id"]
                    mes = message["message"]
                    req["messages"].append(
                        {"from": from_id, "to": to_id, "message": mes}
                    )
                await self._agent._client.social_service.Send(req)
