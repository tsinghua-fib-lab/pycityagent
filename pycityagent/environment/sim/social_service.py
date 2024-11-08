from typing import Any, Awaitable, Coroutine, cast, Union, Dict

import grpc
from google.protobuf.json_format import ParseDict
from pycityproto.city.social.v1 import social_service_pb2 as social_service
from pycityproto.city.social.v1 import social_service_pb2_grpc as social_grpc

from ..utils.protobuf import async_parse

__all__ = ["SocialService"]


class SocialService:
    """
    城市模拟社交服务
    City simulation social service
    """

    def __init__(self, aio_channel: grpc.aio.Channel):
        self._aio_stub = social_grpc.SocialServiceStub(aio_channel)

    def Send(
        self, req: Union[social_service.SendRequest, dict], dict_return: bool = True
    ) -> Coroutine[Any, Any, Union[Dict[str, Any], social_service.SendResponse]]:
        """
        发送消息
        Send message

        Args:
        - req (dict): https://cityproto.sim.fiblab.net/#city.social.v1.SendRequest

        Returns:
        - https://cityproto.sim.fiblab.net/#city.social.v1.SendResponse
        """
        if type(req) != social_service.SendRequest:
            req = ParseDict(req, social_service.SendRequest())
        res = cast(Awaitable[social_service.SendResponse], self._aio_stub.Send(req))
        return async_parse(res, dict_return)

    def Receive(
        self, req: Union[social_service.ReceiveRequest, dict], dict_return: bool = True
    ) -> Coroutine[Any, Any, Union[Dict[str, Any], social_service.ReceiveResponse]]:
        """
        接收消息
        Receive message
        
        Args:
        - req (dict): https://cityproto.sim.fiblab.net/#city.social.v1.ReceiveRequest

        Returns:
        - https://cityproto.sim.fiblab.net/#city.social.v1.ReceiveResponse
        """
        if type(req) != social_service.ReceiveRequest:
            req = ParseDict(req, social_service.ReceiveRequest())
        res = cast(
            Awaitable[social_service.ReceiveResponse], self._aio_stub.Receive(req)
        )
        return async_parse(res, dict_return)
