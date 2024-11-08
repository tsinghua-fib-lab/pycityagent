from typing import Any, Awaitable, Coroutine, cast, Union, Dict

import grpc
from google.protobuf.json_format import ParseDict
from pycityproto.city.map.v2 import road_service_pb2 as road_service
from pycityproto.city.map.v2 import road_service_pb2_grpc as road_grpc

from ..utils.protobuf import async_parse

__all__ = ["RoadService"]


class RoadService:
    """
    交通模拟road服务
    Traffic simulation road service
    """

    def __init__(self, aio_channel: grpc.aio.Channel):
        self._aio_stub = road_grpc.RoadServiceStub(aio_channel)

    def GetRoad(
        self, req: Union[road_service.GetRoadRequest, dict], dict_return: bool = True
    ) -> Coroutine[Any, Any, Union[Dict[str, Any], road_service.GetRoadResponse]]:
        """
        查询道路信息
        Query road information
        
        Args:
        - req (dict): https://cityproto.sim.fiblab.net/#city.map.v2.GetRoadRequest

        Returns:
        - https://cityproto.sim.fiblab.net/#city.map.v2.GetRoadResponse
        """
        if type(req) != road_service.GetRoadRequest:
            req = ParseDict(req, road_service.GetRoadRequest())
        res = cast(Awaitable[road_service.GetRoadResponse], self._aio_stub.GetRoad(req))
        return async_parse(res, dict_return)
