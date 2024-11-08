from typing import Any, Awaitable, Coroutine, cast, Union, Dict

import grpc
from google.protobuf.json_format import ParseDict
from pycityproto.city.clock.v1 import clock_service_pb2 as clock_service
from pycityproto.city.clock.v1 import clock_service_pb2_grpc as clock_grpc

from ..utils.protobuf import async_parse

__all__ = ["ClockService"]


class ClockService:
    """
    城市模拟时间服务
    City simulation clock service
    """

    def __init__(self, aio_channel: grpc.aio.Channel):
        self._aio_stub = clock_grpc.ClockServiceStub(aio_channel)

    def Now(
        self,
        req: Union[clock_service.NowRequest, dict],
        dict_return: bool = True,
    ) -> Coroutine[Any, Any, Union[Dict[str, Any], clock_service.NowResponse]]:
        """
        获取当前的模拟时间请求
        Getting current simulation clock

        Args:
        - req (dict): https://cityproto.sim.fiblab.net/#city.clock.v1.NowRequest

        Returns:
        - https://cityproto.sim.fiblab.net/#city.clock.v1.NowResponse
        """
        if type(req) != clock_service.NowRequest:
            req = ParseDict(req, clock_service.NowRequest())
        res = cast(
            Awaitable[clock_service.NowResponse],
            self._aio_stub.Now(req),
        )
        return async_parse(res, dict_return)
