import warnings
from collections.abc import Awaitable, Coroutine
from typing import Any, Union, cast

import grpc
from google.protobuf.json_format import ParseDict
from mosstool.trip.generator import default_person_template_generator
from mosstool.util.format_converter import pb2dict
from pycityproto.city.person.v2 import person_pb2 as person_pb2
from pycityproto.city.person.v2 import person_service_pb2 as person_service
from pycityproto.city.person.v2 import person_service_pb2_grpc as person_grpc

from ..utils.protobuf import async_parse

__all__ = ["PersonService"]


class PersonService:
    """
    交通模拟person服务
    Traffic simulation person service
    """

    def __init__(self, aio_channel: grpc.aio.Channel):
        self._aio_stub = person_grpc.PersonServiceStub(aio_channel)

    @staticmethod
    def default_person() -> person_pb2.Person:
        """
        获取person基本模板
        Get person basic template

        需要补充的字段有person.home,person.schedules,person.labels
        The fields that need to be supplemented are person.home, person.schedules, person.labels
        """
        person = default_person_template_generator()
        return person

    @staticmethod
    def default_dict_person() -> dict:
        """
        获取person基本模板，字典格式
        Get person basic template in dict format.

        需要补充的字段有person.home,person.schedules,person.labels
        The fields that need to be supplemented are person.home, person.schedules, person.labels
        """
        person = default_person_template_generator()
        return pb2dict(person)

    def GetPerson(
        self,
        req: Union[person_service.GetPersonRequest, dict],
        dict_return: bool = True,
    ) -> Coroutine[Any, Any, Union[dict[str, Any], person_service.GetPersonResponse]]:
        """
        获取person信息
        Get person information

        Args:
        - req (dict): https://cityproto.sim.fiblab.net/#city.person.v2.GetPersonRequest

        Returns:
        - https://cityproto.sim.fiblab.net/#city.person.v2.GetPersonResponse
        """
        if type(req) != person_service.GetPersonRequest:
            req = ParseDict(req, person_service.GetPersonRequest())
        res = cast(
            Awaitable[person_service.GetPersonResponse], self._aio_stub.GetPerson(req)
        )
        return async_parse(res, dict_return)

    def AddPerson(
        self,
        req: Union[person_service.AddPersonRequest, dict],
        dict_return: bool = True,
    ) -> Coroutine[Any, Any, Union[dict[str, Any], person_service.AddPersonResponse]]:
        """
        新增person
        Add a new person

        Args:
        - req (dict): https://cityproto.sim.fiblab.net/#city.person.v2.AddPersonRequest

        Returns:
        - https://cityproto.sim.fiblab.net/#city.person.v2.AddPersonResponse
        """
        if type(req) != person_service.AddPersonRequest:
            req = ParseDict(req, person_service.AddPersonRequest())
        res = cast(
            Awaitable[person_service.AddPersonResponse], self._aio_stub.AddPerson(req)
        )
        return async_parse(res, dict_return)

    def SetSchedule(
        self,
        req: Union[person_service.SetScheduleRequest, dict],
        dict_return: bool = True,
    ) -> Coroutine[Any, Any, Union[dict[str, Any], person_service.SetScheduleResponse]]:
        """
        修改person的schedule
        set person's schedule

        Args:
        - req (dict): https://cityproto.sim.fiblab.net/#city.person.v2.SetScheduleRequest

        Returns:
        - https://cityproto.sim.fiblab.net/#city.person.v2.SetScheduleResponse
        """
        if type(req) != person_service.SetScheduleRequest:
            req = ParseDict(req, person_service.SetScheduleRequest())
        res = cast(
            Awaitable[person_service.SetScheduleResponse],
            self._aio_stub.SetSchedule(req),
        )
        return async_parse(res, dict_return)

    def GetPersons(
        self,
        req: Union[person_service.GetPersonsRequest, dict],
        dict_return: bool = True,
    ) -> Coroutine[Any, Any, Union[dict[str, Any], person_service.GetPersonsResponse]]:
        """
        获取多个person信息
        Get information of multiple persons

        Args:
        - req (dict): https://cityproto.sim.fiblab.net/#city.person.v2.GetPersonsRequest

        Returns:
        - https://cityproto.sim.fiblab.net/#city.person.v2.GetPersonsResponse
        """
        if type(req) != person_service.GetPersonsRequest:
            req = ParseDict(req, person_service.GetPersonsRequest())
        res = cast(
            Awaitable[person_service.GetPersonsResponse],
            self._aio_stub.GetPersons(req),
        )
        return async_parse(res, dict_return)

    def GetPersonByLongLatBBox(
        self,
        req: Union[person_service.GetPersonByLongLatBBoxRequest, dict],
        dict_return: bool = True,
    ) -> Coroutine[
        Any, Any, Union[dict[str, Any], person_service.GetPersonByLongLatBBoxResponse]
    ]:
        """
        获取特定区域内的person
        Get persons in a specific region

        Args:
        - req (dict): https://cityproto.sim.fiblab.net/#city.person.v2.GetPersonByLongLatBBoxRequest

        Returns:
        - https://cityproto.sim.fiblab.net/#city.person.v2.GetPersonByLongLatBBoxResponse
        """
        if type(req) != person_service.GetPersonByLongLatBBoxRequest:
            req = ParseDict(req, person_service.GetPersonByLongLatBBoxRequest())
        res = cast(
            Awaitable[person_service.GetPersonByLongLatBBoxResponse],
            self._aio_stub.GetPersonByLongLatBBox(req),
        )
        return async_parse(res, dict_return)

    def GetAllVehicles(
        self,
        req: Union[person_service.GetAllVehiclesRequest, dict],
        dict_return: bool = True,
    ) -> Coroutine[
        Any, Any, Union[dict[str, Any], person_service.GetAllVehiclesResponse]
    ]:
        """
        获取所有车辆
        Get all vehicles

        Args:
        - req (dict): https://cityproto.sim.fiblab.net/#city.person.v2.GetAllVehiclesRequest

        Returns:
        - https://cityproto.sim.fiblab.net/#city.person.v2.GetAllVehiclesResponse
        """
        if type(req) != person_service.GetAllVehiclesRequest:
            req = ParseDict(req, person_service.GetAllVehiclesRequest())
        res = cast(
            Awaitable[person_service.GetAllVehiclesResponse],
            self._aio_stub.GetAllVehicles(req),
        )
        return async_parse(res, dict_return)

    def ResetPersonPosition(
        self,
        req: Union[person_service.ResetPersonPositionRequest, dict],
        dict_return: bool = True,
    ) -> Coroutine[
        Any, Any, Union[dict[str, Any], person_service.ResetPersonPositionResponse]
    ]:
        """
        重置人的位置（将停止当前正在进行的出行，转为sleep状态）
        Reset person's position (stop the current trip and switch to sleep status)

        Args:
        - req (dict): https://cityproto.sim.fiblab.net/#city.person.v2.ResetPersonPositionRequest

        Returns:
        - https://cityproto.sim.fiblab.net/#city.person.v2.ResetPersonPositionResponse
        """
        if type(req) != person_service.ResetPersonPositionRequest:
            req = ParseDict(req, person_service.ResetPersonPositionRequest())
        res = cast(
            Awaitable[person_service.ResetPersonPositionResponse],
            self._aio_stub.ResetPersonPosition(req),
        )
        return async_parse(res, dict_return)

    # RL接口

    def SetControlledVehicleIDs(
        self,
        req: Union[person_service.SetControlledVehicleIDsRequest, dict],
        dict_return: bool = True,
    ) -> Coroutine[
        Any, Any, Union[dict[str, Any], person_service.SetControlledVehicleIDsResponse]
    ]:
        """
        设置由外部控制行为的vehicle
        Set controlled vehicle ID

        Args:
        - req (dict): https://cityproto.sim.fiblab.net/#city.person.v2.SetControlledVehicleIDsRequest

        Returns:
        - https://cityproto.sim.fiblab.net/#city.person.v2.SetControlledVehicleIDsResponse
        """
        if type(req) != person_service.SetControlledVehicleIDsRequest:
            req = ParseDict(req, person_service.SetControlledVehicleIDsRequest())
        res = cast(
            Awaitable[person_service.SetControlledVehicleIDsResponse],
            self._aio_stub.SetControlledVehicleIDs(req),
        )
        return async_parse(res, dict_return)

    def FetchControlledVehicleEnvs(
        self,
        req: Union[person_service.FetchControlledVehicleEnvsRequest, dict],
        dict_return: bool = True,
    ) -> Coroutine[
        Any,
        Any,
        Union[dict[str, Any], person_service.FetchControlledVehicleEnvsResponse],
    ]:
        """
        获取由外部控制行为的vehicle的环境信息
        Fetch controlled vehicle environment information

        Args:
        - req (dict): https://cityproto.sim.fiblab.net/#city.person.v2.FetchControlledVehicleEnvsRequest

        Returns:
        - https://cityproto.sim.fiblab.net/#city.person.v2.FetchControlledVehicleEnvsResponse
        """
        if type(req) != person_service.FetchControlledVehicleEnvsRequest:
            req = ParseDict(req, person_service.FetchControlledVehicleEnvsRequest())
        res = cast(
            Awaitable[person_service.FetchControlledVehicleEnvsResponse],
            self._aio_stub.FetchControlledVehicleEnvs(req),
        )
        return async_parse(res, dict_return)

    def SetControlledVehicleActions(
        self,
        req: Union[person_service.SetControlledVehicleActionsRequest, dict],
        dict_return: bool = True,
    ) -> Coroutine[
        Any,
        Any,
        Union[dict[str, Any], person_service.SetControlledVehicleActionsResponse],
    ]:
        """
        设置由外部控制行为的vehicle的行为
        Set controlled vehicle actions

        Args:
        - req (dict): https://cityproto.sim.fiblab.net/#city.person.v2.SetControlledVehicleActionsRequest

        Returns:
        - https://cityproto.sim.fiblab.net/#city.person.v2.SetControlledVehicleActionsResponse
        """
        if type(req) != person_service.SetControlledVehicleActionsRequest:
            req = ParseDict(req, person_service.SetControlledVehicleActionsRequest())
        res = cast(
            Awaitable[person_service.SetControlledVehicleActionsResponse],
            self._aio_stub.SetControlledVehicleActions(req),
        )
        return async_parse(res, dict_return)
