from collections.abc import Awaitable, Coroutine
from typing import Any, Union, cast

import grpc
from pycityproto.city.pause.v1 import pause_service_pb2 as pause_service
from pycityproto.city.pause.v1 import pause_service_pb2_grpc as pause_grpc

from ..utils.protobuf import async_parse

__all__ = ["PauseService"]


class PauseService:
    """
    城市模拟暂停服务
    City simulation pause service
    """

    def __init__(self, aio_channel: grpc.aio.Channel):
        self._aio_stub = pause_grpc.PauseServiceStub(aio_channel)

    async def pause(
        self,
    ) -> Awaitable[Union[dict[str, Any], pause_service.PauseResponse]]:
        """
        暂停模拟
        Pause the simulation

        - **Args**:
        - req (dict): https://cityproto.readthedocs.io/en/latest/docs.html#pauserequest

        - **Returns**:
        - https://cityproto.readthedocs.io/en/latest/docs.html#pauseresponse
        """
        req = pause_service.PauseRequest()
        res = cast(
            Awaitable[pause_service.PauseResponse],
            self._aio_stub.Pause(req),
        )
        return res
    
    async def resume(
        self,
    ) -> Awaitable[Union[dict[str, Any], pause_service.ResumeResponse]]:
        """
        恢复模拟
        Resume the simulation

        - **Args**:
        - req (dict): https://cityproto.readthedocs.io/en/latest/docs.html#resumerequest

        - **Returns**:
        - https://cityproto.readthedocs.io/en/latest/docs.html#resumeresponse
        """
        req = pause_service.ResumeRequest()
        res = cast(
            Awaitable[pause_service.ResumeResponse],
            self._aio_stub.Resume(req),
        )
        return res
