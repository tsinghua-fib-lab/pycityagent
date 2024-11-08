from typing import Any, Awaitable, Coroutine, cast, Union, Dict

import grpc
from google.protobuf.json_format import ParseDict
from pycityproto.city.economy.v1 import org_service_pb2 as org_service
from pycityproto.city.economy.v1 import org_service_pb2_grpc as org_grpc
from pycityproto.city.economy.v1 import person_service_pb2 as person_service
from pycityproto.city.economy.v1 import person_service_pb2_grpc as person_grpc

from ..utils.protobuf import async_parse

__all__ = ["EconomyPersonService", "EconomyOrgService"]


class EconomyPersonService:
    """
    城市模拟经济服务（个人）
    City simulation economic service (personal)
    """

    def __init__(self, aio_channel: grpc.aio.Channel):
        self._aio_stub = person_grpc.PersonServiceStub(aio_channel)

    def GetPerson(
        self,
        req: Union[person_service.GetPersonRequest, dict],
        dict_return: bool = True,
    ) -> Coroutine[Any, Any, Union[Dict[str, Any], person_service.GetPersonResponse]]:
        """
        批量查询人的经济情况（资金、雇佣关系）
        Query person’s economic situation (funds, employment relationship) in batches
        
        Args:
        - req (dict): https://cityproto.sim.fiblab.net/#city.economy.v1.GetPersonRequest

        Returns:
        - https://cityproto.sim.fiblab.net/#city.economy.v1.GetPersonResponse
        """
        if type(req) != person_service.GetPersonRequest:
            req = ParseDict(req, person_service.GetPersonRequest())
        res = cast(
            Awaitable[person_service.GetPersonResponse], self._aio_stub.GetPerson(req)
        )
        return async_parse(res, dict_return)

    def UpdatePersonMoney(
        self,
        req: Union[person_service.UpdatePersonMoneyRequest, dict],
        dict_return: bool = True,
    ) -> Coroutine[
        Any, Any, Union[Dict[str, Any], person_service.UpdatePersonMoneyResponse]
    ]:
        """
        批量修改人的资金
        Modify person’s money in batches

        Args:
        - req (dict): https://cityproto.sim.fiblab.net/#city.economy.v1.UpdatePersonMoneyRequest

        Returns:
        - https://cityproto.sim.fiblab.net/#city.economy.v1.UpdatePersonMoneyResponse
        """
        if type(req) != person_service.UpdatePersonMoneyRequest:
            req = ParseDict(req, person_service.UpdatePersonMoneyRequest())
        res = cast(
            Awaitable[person_service.UpdatePersonMoneyResponse],
            self._aio_stub.UpdatePersonMoney(req),
        )
        return async_parse(res, dict_return)


class EconomyOrgService:
    """
    城市模拟经济服务（组织）
    City simulation economic service (organizational)
    """

    def __init__(self, aio_channel: grpc.aio.Channel):
        self._aio_stub = org_grpc.OrgServiceStub(aio_channel)

    def GetOrg(
        self, req: Union[org_service.GetOrgRequest, dict], dict_return: bool = True
    ) -> Coroutine[Any, Any, Union[Dict[str, Any], org_service.GetOrgResponse]]:
        """
        批量查询组织的经济情况（员工、岗位、资金、货物）
        Query the economic status of the organization (employees, positions, funds, goods) in batches

        Args:
        - req (dict): https://cityproto.sim.fiblab.net/#city.economy.v1.GetOrgRequest

        Returns:
        - https://cityproto.sim.fiblab.net/#city.economy.v1.GetOrgResponse
        """
        if type(req) != org_service.GetOrgRequest:
            req = ParseDict(req, org_service.GetOrgRequest())
        res = cast(Awaitable[org_service.GetOrgResponse], self._aio_stub.GetOrg(req))
        return async_parse(res, dict_return)

    def UpdateOrgMoney(
        self,
        req: Union[org_service.UpdateOrgMoneyRequest, dict],
        dict_return: bool = True,
    ) -> Coroutine[Any, Any, Union[Dict[str, Any], org_service.UpdateOrgMoneyResponse]]:
        """
        批量修改组织的资金
        Modify organization’s money in batches

        Args:
        - req (dict): https://cityproto.sim.fiblab.net/#city.economy.v1.UpdateOrgMoneyRequest

        Returns:
        - https://cityproto.sim.fiblab.net/#city.economy.v1.UpdateOrgMoneyResponse
        """
        if type(req) != org_service.UpdateOrgMoneyRequest:
            req = ParseDict(req, org_service.UpdateOrgMoneyRequest())
        res = cast(
            Awaitable[org_service.UpdateOrgMoneyResponse],
            self._aio_stub.UpdateOrgMoney(req),
        )
        return async_parse(res, dict_return)

    def UpdateOrgGoods(
        self,
        req: Union[org_service.UpdateOrgGoodsRequest, dict],
        dict_return: bool = True,
    ) -> Coroutine[Any, Any, Union[Dict[str, Any], org_service.UpdateOrgGoodsResponse]]:
        """
        批量修改组织的货物
        Modify organization’s goods in batches

        Args:
        - req (dict): https://cityproto.sim.fiblab.net/#city.economy.v1.UpdateOrgGoodsRequest

        Returns:
        - https://cityproto.sim.fiblab.net/#city.economy.v1.UpdateOrgGoodsResponse
        """
        if type(req) != org_service.UpdateOrgGoodsRequest:
            req = ParseDict(req, org_service.UpdateOrgGoodsRequest())
        res = cast(
            Awaitable[org_service.UpdateOrgGoodsResponse],
            self._aio_stub.UpdateOrgGoods(req),
        )
        return async_parse(res, dict_return)

    def UpdateOrgEmployee(
        self,
        req: Union[org_service.UpdateOrgEmployeeRequest, dict],
        dict_return: bool = True,
    ) -> Coroutine[
        Any, Any, Union[Dict[str, Any], org_service.UpdateOrgEmployeeResponse]
    ]:
        """
        批量修改组织的员工
        Modify organization’s emplpyees in batches

        Args:
        - req (dict): https://cityproto.sim.fiblab.net/#city.economy.v1.UpdateOrgEmployeeRequest

        Returns:
        - https://cityproto.sim.fiblab.net/#city.economy.v1.UpdateOrgEmployeeResponse
        """
        if type(req) != org_service.UpdateOrgEmployeeRequest:
            req = ParseDict(req, org_service.UpdateOrgEmployeeRequest())
        res = cast(
            Awaitable[org_service.UpdateOrgEmployeeResponse],
            self._aio_stub.UpdateOrgEmployee(req),
        )
        return async_parse(res, dict_return)

    def UpdateOrgJob(
        self,
        req: Union[org_service.UpdateOrgJobRequest, dict],
        dict_return: bool = True,
    ) -> Coroutine[Any, Any, Union[Dict[str, Any], org_service.UpdateOrgJobResponse]]:
        """
        批量修改组织的岗位
        Modify organization’s jobs in batches

        Args:
        - req (dict): https://cityproto.sim.fiblab.net/#city.economy.v1.UpdateOrgJobRequest

        Returns:
        - https://cityproto.sim.fiblab.net/#city.economy.v1.UpdateOrgJobResponse
        """
        if type(req) != org_service.UpdateOrgJobRequest:
            req = ParseDict(req, org_service.UpdateOrgJobRequest())
        res = cast(
            Awaitable[org_service.UpdateOrgJobResponse],
            self._aio_stub.UpdateOrgJob(req),
        )
        return async_parse(res, dict_return)
