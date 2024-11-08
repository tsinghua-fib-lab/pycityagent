from typing import Any, Awaitable, Coroutine, cast, Union, Dict

import grpc
from google.protobuf.json_format import ParseDict
from pycityproto.city.map.v2 import aoi_service_pb2 as aoi_service
from pycityproto.city.map.v2 import aoi_service_pb2_grpc as aoi_grpc

from ..utils.protobuf import async_parse

__all__ = ["AoiService"]


class AoiService:
    """
    aoi服务
    AOI service
    """

    def __init__(self, aio_channel: grpc.aio.Channel):
        self._aio_stub = aoi_grpc.AoiServiceStub(aio_channel)

    def GetAoi(
        self, req: Union[aoi_service.GetAoiRequest, dict], dict_return: bool = True
    ) -> Coroutine[Any, Any, Union[Dict[str, Any], aoi_service.GetAoiResponse]]:
        """
        获取AOI信息
        get AOI information
        
        Args:
        - req (dict): https://cityproto.sim.fiblab.net/#city.map.v2.GetAoiRequest

        Returns:
        - https://cityproto.sim.fiblab.net/#city.map.v2.GetAoiResponse
        """
        if type(req) != aoi_service.GetAoiRequest:
            req = ParseDict(req, aoi_service.GetAoiRequest())
        res = cast(Awaitable[aoi_service.GetAoiResponse], self._aio_stub.GetAoi(req))
        return async_parse(res, dict_return)
