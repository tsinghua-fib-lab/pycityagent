import warnings
import grpc

from .clock_service import ClockService
from .person_service import PersonService
from .aoi_service import AoiService
from .lane_service import LaneService
from .road_service import RoadService
from .social_service import SocialService
from .light_service import LightService
from .pause_service import PauseService
from ..utils.grpc import create_aio_channel

__all__ = ["CityClient"]


class CityClient:
    """
    模拟器接口
    Simulator interface
    """

    NAME = "city"

    def __init__(
        self,
        url: str,
        secure: bool = False,
    ):
        """
        - **Args**:
            - `url` (`str`): 模拟器server的地址。The address of the emulator server.
            - `secure` (`bool`, `optional`): 是否使用安全连接. Defaults to False. Whether to use a secure connection. Defaults to False.
        """
        aio_channel = create_aio_channel(url, secure)
        self._clock_service = ClockService(aio_channel)
        self._lane_service = LaneService(aio_channel)
        self._person_service = PersonService(aio_channel)
        self._aoi_service = AoiService(aio_channel)
        self._road_service = RoadService(aio_channel)
        self._social_service = SocialService(aio_channel)
        self._light_service = LightService(aio_channel)
        self._pause_service = PauseService(aio_channel)

    @property
    def clock_service(self):
        """
        模拟器时间服务子模块
        Simulator time service submodule
        """
        return self._clock_service

    @property
    def pause_service(self):
        """
        模拟器暂停服务子模块
        Simulator pause service submodule
        """
        return self._pause_service

    @property
    def lane_service(self):
        """
        模拟器lane服务子模块
        Simulator lane service submodule
        """
        return self._lane_service

    @property
    def person_service(self):
        """
        模拟器智能体服务子模块
        Simulator agent service submodule
        """
        return self._person_service

    @property
    def aoi_service(self):
        """
        模拟器AOI服务子模块
        Simulator AOI service submodule
        """
        return self._aoi_service

    @property
    def road_service(self):
        """
        模拟器road服务子模块
        Simulator road service submodule
        """
        return self._road_service

    @property
    def social_service(self):
        """
        模拟器social服务子模块
        Simulator social service submodule
        """
        return self._social_service

    @property
    def light_service(self):
        """
        模拟器红绿灯服务子模块
        Simulator traffic light service submodule
        """
        return self._light_service
