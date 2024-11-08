from typing import Any, Awaitable, Coroutine, cast, Union, Dict

import grpc
from google.protobuf.json_format import ParseDict
from pycityproto.city.map.v2 import lane_service_pb2 as lane_service
from pycityproto.city.map.v2 import lane_service_pb2_grpc as lane_grpc

from ..utils.protobuf import async_parse

__all__ = ["LaneService"]


class LaneService:
    """
    交通模拟lane服务
    Traffic simulation lane service
    """

    def __init__(self, aio_channel: grpc.aio.Channel):
        self._aio_stub = lane_grpc.LaneServiceStub(aio_channel)

    def GetLane(
        self, req: Union[lane_service.GetLaneRequest, dict], dict_return: bool = True
    ) -> Coroutine[Any, Any, Union[Dict[str, Any], lane_service.GetLaneResponse]]:
        """
        获取Lane的信息
        Get Lane's information

        Args:
        - req (dict): https://cityproto.sim.fiblab.net/#city.map.v2.GetLaneRequest

        Returns:
        - https://cityproto.sim.fiblab.net/#city.map.v2.GetLaneResponse
        """
        if type(req) != lane_service.GetLaneRequest:
            req = ParseDict(req, lane_service.GetLaneRequest())
        res = cast(Awaitable[lane_service.GetLaneResponse], self._aio_stub.GetLane(req))
        return async_parse(res, dict_return)

    def SetLaneMaxV(
        self,
        req: Union[lane_service.SetLaneMaxVRequest, dict],
        dict_return: bool = True,
    ) -> Coroutine[Any, Any, Union[Dict[str, Any], lane_service.SetLaneMaxVResponse]]:
        """
        设置Lane的最大速度（限速）
        Set the maximum speed of Lane (speed limit)

        Args:
        - req (dict): https://cityproto.sim.fiblab.net/#city.map.v2.SetLaneMaxVRequest

        Returns:
        - https://cityproto.sim.fiblab.net/#city.map.v2.SetLaneMaxVResponse
        """
        if type(req) != lane_service.SetLaneMaxVRequest:
            req = ParseDict(req, lane_service.SetLaneMaxVRequest())
        res = cast(
            Awaitable[lane_service.SetLaneMaxVResponse], self._aio_stub.SetLaneMaxV(req)
        )
        return async_parse(res, dict_return)

    def SetLaneRestriction(
        self,
        req: Union[lane_service.SetLaneRestrictionRequest, dict],
        dict_return: bool = True,
    ) -> Coroutine[
        Any, Any, Union[Dict[str, Any], lane_service.SetLaneRestrictionResponse]
    ]:
        """
        设置Lane的限制
        Set the restriction of Lane

        Args:
        - req (dict): https://cityproto.sim.fiblab.net/#city.map.v2.SetLaneRestrictionRequest

        Returns:
        - https://cityproto.sim.fiblab.net/#city.map.v2.SetLaneRestrictionResponse
        """
        if type(req) != lane_service.SetLaneRestrictionRequest:
            req = ParseDict(req, lane_service.SetLaneRestrictionRequest())
        res = cast(
            Awaitable[lane_service.SetLaneRestrictionResponse],
            self._aio_stub.SetLaneRestriction(req),
        )
        return async_parse(res, dict_return)

    def GetLaneByLongLatBBox(
        self,
        req: Union[lane_service.GetLaneByLongLatBBoxRequest, dict],
        dict_return: bool = True,
    ) -> Coroutine[
        Any, Any, Union[Dict[str, Any], lane_service.GetLaneByLongLatBBoxResponse]
    ]:
        """
        获取特定区域内的Lane的信息
        Get lane information in a specific region

        Args:
        - req (dict): https://cityproto.sim.fiblab.net/#city.map.v2.GetLaneByLongLatBBoxRequest

        Returns:
        - https://cityproto.sim.fiblab.net/#city.map.v2.GetLaneByLongLatBBoxResponse
        """
        if type(req) != lane_service.GetLaneByLongLatBBoxRequest:
            req = ParseDict(req, lane_service.GetLaneByLongLatBBoxRequest())
        res = cast(
            Awaitable[lane_service.GetLaneByLongLatBBoxResponse],
            self._aio_stub.GetLaneByLongLatBBox(req),
        )
        return async_parse(res, dict_return)
