from typing import Any, Awaitable, Coroutine, cast, Union, Dict

import grpc
from google.protobuf.json_format import ParseDict
from pycityproto.city.map.v2 import traffic_light_service_pb2 as light_service
from pycityproto.city.map.v2 import traffic_light_service_pb2_grpc as light_grpc

from ..utils.protobuf import async_parse

__all__ = ["LightService"]


class LightService:
    """
    城市模拟信控服务
    City simulation traffic light service
    """

    def __init__(self, aio_channel: grpc.aio.Channel):
        self._aio_stub = light_grpc.TrafficLightServiceStub(aio_channel)

    def GetTrafficLight(
        self,
        req: Union[light_service.GetTrafficLightRequest, Dict[str, Any]],
        dict_return: bool = True,
    ) -> Coroutine[
        Any, Any, Union[Dict[str, Any], light_service.GetTrafficLightResponse]
    ]:
        """
        获取路口的红绿灯信息
        Get traffic light information

        Args:
        - req (dict): https://cityproto.sim.fiblab.net/#city.traffic.v1.GetTrafficLightRequest

        Returns:
        - https://cityproto.sim.fiblab.net/#city.traffic.v1.GetTrafficLightResponse
        """
        if type(req) != light_service.GetTrafficLightRequest:
            req = ParseDict(req, light_service.GetTrafficLightRequest())
        res = cast(
            Awaitable[light_service.GetTrafficLightResponse],
            self._aio_stub.GetTrafficLight(req),
        )
        return async_parse(res, dict_return)

    def SetTrafficLight(
        self,
        req: Union[light_service.SetTrafficLightRequest, Dict[str, Any]],
        dict_return: bool = True,
    ) -> Coroutine[
        Any, Any, Union[Dict[str, Any], light_service.SetTrafficLightResponse]
    ]:
        """
        设置路口的红绿灯信息
        Set traffic light information

        Args:
        - req (dict): https://cityproto.sim.fiblab.net/#city.traffic.v1.SetTrafficLightRequest

        Returns:
        - https://cityproto.sim.fiblab.net/#city.traffic.v1.SetTrafficLightResponse
        """
        if type(req) != light_service.SetTrafficLightRequest:
            req = ParseDict(req, light_service.SetTrafficLightRequest())
        res = cast(
            Awaitable[light_service.SetTrafficLightResponse],
            self._aio_stub.SetTrafficLight(req),
        )
        return async_parse(res, dict_return)

    def SetTrafficLightPhase(
        self,
        req: Union[light_service.SetTrafficLightPhaseRequest, dict],
        dict_return: bool = True,
    ) -> Coroutine[
        Any, Any, Union[Dict[str, Any], light_service.SetTrafficLightPhaseResponse]
    ]:
        """
        设置路口的红绿灯相位
        Set traffic light phase

        Args:
        - req (dict): https://cityproto.sim.fiblab.net/#city.traffic.v1.SetTrafficLightPhaseRequest

        Returns:
        - https://cityproto.sim.fiblab.net/#city.traffic.v1.SetTrafficLightPhaseResponse
        """
        if type(req) != light_service.SetTrafficLightPhaseRequest:
            req = ParseDict(req, light_service.SetTrafficLightPhaseRequest())
        res = cast(
            Awaitable[light_service.SetTrafficLightPhaseResponse],
            self._aio_stub.SetTrafficLightPhase(req),
        )
        return async_parse(res, dict_return)

    def SetTrafficLightStatus(
        self,
        req: Union[light_service.SetTrafficLightStatusRequest, dict],
        dict_return: bool = True,
    ) -> Coroutine[
        Any, Any, Union[Dict[str, Any], light_service.SetTrafficLightStatusResponse]
    ]:
        """
        设置路口的红绿灯状态
        Set traffic light status

        Args:
        - req (dict): https://cityproto.sim.fiblab.net/#city.traffic.v1.SetTrafficLightStatusRequest

        Returns:
        - https://cityproto.sim.fiblab.net/#city.traffic.v1.SetTrafficLightStatusResponse
        """
        if type(req) != light_service.SetTrafficLightStatusRequest:
            req = ParseDict(req, light_service.SetTrafficLightStatusRequest())
        res = cast(
            Awaitable[light_service.SetTrafficLightStatusResponse],
            self._aio_stub.SetTrafficLightStatus(req),
        )
        return async_parse(res, dict_return)
