from typing import Callable, Optional, Any
from pycitysim.apphub import AgentMessage
from .action import HubAction
from PIL.Image import Image

class SendUserMessage(HubAction):
    """
    发送用户可见信息
    Send messages to user
    """
    def __init__(self, agent, source: str = None, before: Callable[[list], Any] = None) -> None:
        super().__init__(agent, source, before)

    async def Forward(self, messages: Optional[list[AgentMessage]] = None):
        if not messages == None:
            self._agent.Hub.Update(messages = messages)
        elif self._source != None:
            messages = self.get_source()
            if messages != None:
                self._agent.Hub.Update(messages = messages)

class SendStreetview(HubAction):
    """
    发送街景图片至前端
    Send streetview to frontend
    """
    def __init__(self, agent, source: str = None, before: Callable[[list], Any] = None) -> None:
        super().__init__(agent, source, before)

    async def Forward(self, images: Optional[list[Image]] = None):
        # TODO: 目前只支持发送一张图片
        if not images == None:
            self._agent.Hub.Update(streetview = images[0])
        elif self._source != None:
            images = self.get_source()
            if images != None:
                self._agent.Hub.Update(streetview = images[0])

class SendPop(HubAction):
    """
    发送Pop信息 - agent头顶气泡信息
    Send pop message to frontend, pop message shows above the target agent
    """
    def __init__(self, agent, source: str = None, before: Callable[[list], Any] = None) -> None:
        super().__init__(agent, source, before)

    async def Forward(self, pop:Optional[str] = None):
        if not pop == None:
            self._agent.Hub.Update(pop = pop)
        elif self._source != None:
            pop = self.get_source()
            if pop != None:
                self._agent.Hub.Update(pop = pop)

class PositionUpdate(HubAction):
    """
    同步当前agent的位置信息
    Send the position of current agent to frontend
    """
    def __init__(self, agent, source: str = None, before: Callable[[list], Any] = None) -> None:
        super().__init__(agent, source, before)

    async def Forward(self, longlat: Optional[list[float]] = None):
        if longlat != None:
            self._agent.Hub.Update(longlat = longlat)
        elif self._source != None:
            longlat = self.get_source()
            if longlat != None:
                self._agent.Hub.Update(longlat = longlat)

class ShowPath(HubAction):
    """
    在地图上展示路径信息
    Show a path in frontend map
    """
    def __init__(self, agent, source: str = None, before: Callable[[list], Any] = None) -> None:
        super().__init__(agent, source, before)

    async def Forward(self):
        # TODO: 相关功能完善
        pass

class ShowPosition(HubAction):
    """
    在地图上展示特定地点
    Show a position in frontend map
    """
    def __init__(self, agent, source: str = None, before: Callable[[list], Any] = None) -> None:
        super().__init__(agent, source, before)

    async def Forward(self):
        # TODO: 相关功能完善
        pass