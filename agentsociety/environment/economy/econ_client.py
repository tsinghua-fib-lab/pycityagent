import asyncio
import logging
import re
import time
from collections.abc import Sequence
from typing import Any, Literal, Union, cast

import grpc
import pycityproto.city.economy.v2.economy_pb2 as economyv2
import pycityproto.city.economy.v2.org_service_pb2 as org_service
import pycityproto.city.economy.v2.org_service_pb2_grpc as org_grpc
from google.protobuf.json_format import MessageToDict

logger = logging.getLogger("agentsociety")

__all__ = [
    "EconomyClient",
]


def _create_aio_channel(server_address: str, secure: bool = False) -> grpc.aio.Channel:
    """
    Create a gRPC asynchronous channel.

    - **Args**:
        - `server_address` (`str`): The address of the server to connect to.
        - `secure` (`bool`, optional): Whether to use a secure connection. Defaults to `False`.

    - **Returns**:
        - `grpc.aio.Channel`: A gRPC asynchronous channel for making RPC calls.

    - **Raises**:
        - `ValueError`: If a secure channel is requested but the server address starts with `http://`.

    - **Description**:
        - This function creates and returns a gRPC asynchronous channel based on the provided server address and security flag.
        - It ensures that if `secure=True`, then the server address does not start with `http://`.
        - If the server address starts with `https://`, it will automatically switch to a secure connection even if `secure=False`.
    """
    if server_address.startswith("http://"):
        server_address = server_address.split("//")[1]
        if secure:
            raise ValueError("secure channel must use `https` or not use `http`")
    elif server_address.startswith("https://"):
        server_address = server_address.split("//")[1]
        if not secure:
            secure = True

    if secure:
        return grpc.aio.secure_channel(server_address, grpc.ssl_channel_credentials())
    else:
        return grpc.aio.insecure_channel(server_address)


class EconomyClient:
    """
    Client side of Economy service.

    - **Description**:
        - This class serves as a client interface to interact with the Economy Simulator via gRPC.
        - It establishes an asynchronous connection and provides methods to communicate with the service.
    """

    def __init__(
        self,
        server_address: str,
    ):
        """
        Initialize the EconomyClient.

        - **Args**:
            - `server_address` (`str`): The address of the Economy server to connect to.

        - **Attributes**:
            - `server_address` (`str`): The address of the Economy server.
            - `_aio_stub` (`OrgServiceStub`): A gRPC stub used to make remote calls to the Economy service.

        - **Description**:
            - Initializes the EconomyClient with the specified server address and security preference.
            - Creates an asynchronous gRPC channel using `_create_aio_channel`.
            - Instantiates a gRPC stub (`_aio_stub`) for interacting with the Economy service.
        """
        self.server_address = server_address

        secure = self.server_address.startswith("https")
        self.secure = secure
        aio_channel = _create_aio_channel(server_address, secure)
        self._aio_stub = org_grpc.OrgServiceStub(aio_channel)
        self._agent_ids = set()
        self._org_ids = set()
        self._log_list = []

    def get_log_list(self):
        return self._log_list

    def clear_log_list(self):
        self._log_list = []

    def __getstate__(self):
        """
        Copy the object's state from self.__dict__ which contains
        all our instance attributes. Always use the dict.copy()
        method to avoid modifying the original state.
        """
        state = self.__dict__.copy()
        # Remove the non-picklable entries.
        del state["_aio_stub"]
        return state

    def __setstate__(self, state):
        """
        Restore instance attributes (i.e., filename and mode) from the
        unpickled state dictionary.
        """
        self.__dict__.update(state)
        # Re-initialize the channel after unpickling
        aio_channel = _create_aio_channel(self.server_address, self.secure)
        self._aio_stub = org_grpc.OrgServiceStub(aio_channel)

    async def get_ids(self):
        """
        Get the ids of agents and orgs
        """
        return self._agent_ids, self._org_ids

    async def set_ids(self, agent_ids: set[int], org_ids: set[int]):
        """
        Set the ids of agents and orgs
        """
        self._agent_ids = agent_ids
        self._org_ids = org_ids

    async def get_agent(
        self, id: Union[list[int], int]
    ) -> Union[dict[str, Any], list[dict[str, Any]]]:
        """
        Get agent by id

        - **Args**:
            - `id` (`Union[list[int], int]`): The id of the agent.

        - **Returns**:
            - `economyv2.Agent`: The agent object.
        """
        start_time = time.time()
        log = {"req": "get_agent", "start_time": start_time, "consumption": 0}
        if isinstance(id, list):
            agents = await self._aio_stub.BatchGet(
                org_service.BatchGetRequest(ids=id, type="agent")
            )
            agent_dicts = MessageToDict(agents, preserving_proto_field_name=True)[
                "agents"
            ]
            log["consumption"] = time.time() - start_time
            self._log_list.append(log)
            return agent_dicts
        else:
            agent = await self._aio_stub.GetAgent(
                org_service.GetAgentRequest(agent_id=id)
            )
            agent_dict: dict = MessageToDict(agent, preserving_proto_field_name=True)[
                "agent"
            ]
            log["consumption"] = time.time() - start_time
            self._log_list.append(log)
            return agent_dict

    async def get_org(
        self, id: Union[list[int], int]
    ) -> Union[dict[str, Any], list[dict[str, Any]]]:
        """
        Get org by id

        - **Args**:
            - `id` (`Union[list[int], int]`): The id of the org.

        - **Returns**:
            - `economyv2.Org`: The org object.
        """
        start_time = time.time()
        log = {"req": "get_org", "start_time": start_time, "consumption": 0}
        if isinstance(id, list):
            orgs = await self._aio_stub.BatchGet(
                org_service.BatchGetRequest(ids=id, type="org")
            )
            org_dicts = MessageToDict(orgs, preserving_proto_field_name=True)["orgs"]
            log["consumption"] = time.time() - start_time
            self._log_list.append(log)
            return org_dicts
        else:
            org = await self._aio_stub.GetOrg(org_service.GetOrgRequest(org_id=id))
            org_dict = MessageToDict(org, preserving_proto_field_name=True)["org"]
            log["consumption"] = time.time() - start_time
            self._log_list.append(log)
            return org_dict

    async def get(
        self,
        id: Union[list[int], int],
        key: str,
    ) -> Any:
        """
        Get specific value

        - **Args**:
            - `id` (`Union[list[int], int]`): The id of `Org` or `Agent`.
            - `key` (`str`): The attribute to fetch.

        - **Returns**:
            - Any
        """
        start_time = time.time()
        log = {"req": "get", "start_time": start_time, "consumption": 0}
        if isinstance(id, Sequence):
            requests = "Org" if id[0] in self._org_ids else "Agent"
            if requests == "Org":
                response = await self.get_org(id)
            else:
                response = await self.get_agent(id)
            results = []
            response = cast(list[dict[str, Any]], response)
            for res in response:
                results.append(res[key])
            log["consumption"] = time.time() - start_time
            self._log_list.append(log)
            return results
        else:
            if id not in self._agent_ids and id not in self._org_ids:
                raise ValueError(f"Invalid id {id}, this id does not exist!")
            request_type = "Org" if id in self._org_ids else "Agent"
            if request_type == "Org":
                response = await self.get_org(id)
            else:
                response = await self.get_agent(id)
            response = cast(dict[str, Any], response)
            log["consumption"] = time.time() - start_time
            self._log_list.append(log)
            return response[key]

    def _merge(self, original_value, key, value):
        try:
            orig_value = original_value[key]
            _orig_type = type(orig_value)
            _new_type = type(value)
        except:
            type_ = type(value)
            _orig_type = type_
            _new_type = type_
            orig_value = type_()
        if _orig_type != _new_type:
            logger.debug(
                f"Inconsistent type of original value {_orig_type.__name__} and to-update value {_new_type.__name__}"
            )
        else:
            if isinstance(orig_value, set):
                orig_value.update(set(value))
                original_value[key] = orig_value
            elif isinstance(orig_value, dict):
                orig_value.update(dict(value))
                original_value[key] = orig_value
            elif isinstance(orig_value, list):
                orig_value.extend(list(value))
                original_value[key] = orig_value
            else:
                logger.warning(
                    f"Type of {type(orig_value)} does not support mode `merge`, using `replace` instead!"
                )

    async def update(
        self,
        id: Union[list[int], int],
        key: str,
        value: Union[Any, list[Any]],
        mode: Union[Literal["replace"], Literal["merge"]] = "replace",
    ) -> Any:
        """
        Update key-value pair

        - **Args**:
            - `id` (`Union[list[int], int]`): The id of `Org` or `Agent`.
            - `key` (`str`): The attribute to update.
            - `value` (`Union[Any, list[Any]]`): The value to update.
            - `mode` (Union[Literal["replace"], Literal["merge"]], optional): Update mode. Defaults to "replace".

        - **Returns**:
            - Any
        """
        start_time = time.time()
        log = {"req": "update", "start_time": start_time, "consumption": 0}
        if isinstance(id, list):
            if not isinstance(value, list):
                raise ValueError(f"Invalid value, the value must be a list!")
            if len(id) != len(value):
                raise ValueError(
                    f"Invalid ids and values, the length of ids and values must be the same!"
                )
            request_type = "Org" if id[0] in self._org_ids else "Agent"
        else:
            if id not in self._agent_ids and id not in self._org_ids:
                raise ValueError(f"Invalid id {id}, this id does not exist!")
            request_type = "Org" if id in self._org_ids else "Agent"
        if request_type == "Org":
            original_value = await self.get_org(id)
        else:
            original_value = await self.get_agent(id)
        if mode == "merge":
            if isinstance(original_value, list):
                for i in range(len(original_value)):
                    self._merge(original_value[i], key, value[i])
            else:
                self._merge(original_value, key, value)
        else:
            if isinstance(original_value, list):
                for i in range(len(original_value)):
                    original_value[i][key] = value[i]
            else:
                original_value[key] = value
        if request_type == "Org":
            if isinstance(original_value, list):
                # batch_update_tasks = []
                # for org in original_value:
                #     batch_update_tasks.append(self._aio_stub.UpdateOrg(
                #         org_service.UpdateOrgRequest(
                #             org=org
                #         )
                #     ))
                # await asyncio.gather(*batch_update_tasks)
                await self._aio_stub.BatchUpdate(
                    org_service.BatchUpdateRequest(orgs=original_value, agents=None)
                )
            else:
                await self._aio_stub.UpdateOrg(
                    org_service.UpdateOrgRequest(org=original_value)
                )
            log["consumption"] = time.time() - start_time
            self._log_list.append(log)
        else:
            if isinstance(original_value, list):
                # batch_update_tasks = []
                # for agent in original_value:
                #     batch_update_tasks.append(self._aio_stub.UpdateAgent(
                #         org_service.UpdateAgentRequest(
                #             agent=agent
                #         )
                #     ))
                # await asyncio.gather(*batch_update_tasks)
                await self._aio_stub.BatchUpdate(
                    org_service.BatchUpdateRequest(orgs=None, agents=original_value)
                )
            else:
                await self._aio_stub.UpdateAgent(
                    org_service.UpdateAgentRequest(agent=original_value)
                )
            log["consumption"] = time.time() - start_time
            self._log_list.append(log)

    async def add_agents(self, configs: Union[list[dict], dict]):
        """
        Add one or more agents to the economy system.

        - **Args**:
            - `configs` (`Union[list[dict], dict]`): A single configuration dictionary or a list of dictionaries,
              each containing the necessary information to create an agent (e.g., id, currency).

        - **Returns**:
            - The method does not explicitly return any value but gathers the responses from adding each agent.

        - **Description**:
            - If a single configuration dictionary is provided, it is converted into a list.
            - For each configuration in the list, a task is created to asynchronously add an agent using the provided configuration.
            - All tasks are executed concurrently, and their results are gathered and returned.
        """
        start_time = time.time()
        log = {"req": "add_agents", "start_time": start_time, "consumption": 0}
        if isinstance(configs, dict):
            configs = [configs]
        for config in configs:
            self._agent_ids.add(config["id"])
        tasks = [
            self._aio_stub.AddAgent(
                org_service.AddAgentRequest(
                    agent=economyv2.Agent(
                        id=config["id"],
                        currency=config.get("currency", 0.0),
                        skill=config.get("skill", 0.0),
                        consumption=config.get("consumption", 0.0),
                        income=config.get("income", 0.0),
                    )
                )
            )
            for config in configs
        ]
        await asyncio.gather(*tasks)
        log["consumption"] = time.time() - start_time
        self._log_list.append(log)

    async def add_orgs(self, configs: Union[list[dict], dict]):
        """
        Add one or more organizations to the economy system.

        - **Args**:
            - `configs` (`Union[List[Dict], Dict]`): A single configuration dictionary or a list of dictionaries,
              each containing the necessary information to create an organization (e.g., id, type, nominal_gdp, etc.).

        - **Returns**:
            - `List`: A list of responses from adding each organization.

        - **Raises**:
            - `KeyError`: If a required field is missing from the config dictionary.

        - **Description**:
            - Ensures `configs` is always a list, even if only one config is provided.
            - For each configuration in the list, creates a task to asynchronously add an organization using the provided configuration.
            - Executes all tasks concurrently and gathers their results.
        """
        start_time = time.time()
        log = {"req": "add_orgs", "start_time": start_time, "consumption": 0}
        if isinstance(configs, dict):
            configs = [configs]
        for config in configs:
            self._org_ids.add(config["id"])
        tasks = [
            self._aio_stub.AddOrg(
                org_service.AddOrgRequest(
                    org=economyv2.Org(
                        id=config["id"],
                        type=config["type"],
                        nominal_gdp=config.get("nominal_gdp", []),
                        real_gdp=config.get("real_gdp", []),
                        unemployment=config.get("unemployment", []),
                        wages=config.get("wages", []),
                        prices=config.get("prices", []),
                        inventory=config.get("inventory", 0),
                        price=config.get("price", 0),
                        currency=config.get("currency", 0.0),
                        interest_rate=config.get("interest_rate", 0.0),
                        bracket_cutoffs=config.get("bracket_cutoffs", []),
                        bracket_rates=config.get("bracket_rates", []),
                        consumption_currency=config.get("consumption_currency", []),
                        consumption_propensity=config.get("consumption_propensity", []),
                        income_currency=config.get("income_currency", []),
                        depression=config.get("depression", []),
                        locus_control=config.get("locus_control", []),
                        working_hours=config.get("working_hours", []),
                        employees=config.get("employees", []),
                        citizens=config.get("citizens", []),
                        demand=config.get("demand", 0),
                        sales=config.get("sales", 0),
                    )
                )
            )
            for config in configs
        ]
        await asyncio.gather(*tasks)
        log["consumption"] = time.time() - start_time
        self._log_list.append(log)

    async def calculate_taxes_due(
        self,
        org_id: int,
        agent_ids: list[int],
        incomes: list[float],
        enable_redistribution: bool,
    ):
        """
        Calculate the taxes due for agents based on their incomes.

        - **Args**:
            - `org_id` (`int`): The ID of the government organization.
            - `agent_ids` (`List[int]`): A list of IDs for the agents whose taxes are being calculated.
            - `incomes` (`List[float]`): A list of income values corresponding to each agent.
            - `enable_redistribution` (`bool`): Flag indicating whether redistribution is enabled.

        - **Returns**:
            - `Tuple[float, List[float]]`: A tuple containing the total taxes due and updated incomes after tax calculation.
        """
        start_time = time.time()
        log = {"req": "calculate_taxes_due", "start_time": start_time, "consumption": 0}
        request = org_service.CalculateTaxesDueRequest(
            government_id=org_id,
            agent_ids=agent_ids,
            incomes=incomes,
            enable_redistribution=enable_redistribution,
        )
        response: org_service.CalculateTaxesDueResponse = (
            await self._aio_stub.CalculateTaxesDue(request)
        )
        log["consumption"] = time.time() - start_time
        self._log_list.append(log)
        return (float(response.taxes_due), list(response.updated_incomes))

    async def calculate_consumption(
        self, org_ids: Union[int, list[int]], agent_id: int, demands: list[int], consumption_accumulation: bool = True
    ):
        """
        Calculate consumption for agents based on their demands.

        - **Args**:
            - `org_ids` (`Union[int, list[int]]`): The ID of the firm providing goods or services.
            - `agent_id` (`int`): The ID of the agent whose consumption is being calculated.
            - `demands` (`List[int]`): A list of demand quantities corresponding to each agent.
            - `consumption_accumulation` (`bool`): Weather accumulation.

        - **Returns**:
            - `Tuple[int, List[float]]`: A tuple containing the remaining inventory and updated currencies for each agent.
        """
        start_time = time.time()
        log = {
            "req": "calculate_consumption",
            "start_time": start_time,
            "consumption": 0,
        }
        if not isinstance(org_ids, Sequence):
            org_ids = [org_ids]
        request = org_service.CalculateConsumptionRequest(
            firm_ids=org_ids,
            agent_id=agent_id,
            demands=demands,
            consumption_accumulation = consumption_accumulation,
        )
        response: org_service.CalculateConsumptionResponse = (
            await self._aio_stub.CalculateConsumption(request)
        )
        log["consumption"] = time.time() - start_time
        self._log_list.append(log)
        if response.success:
            return response.actual_consumption
        else:
            return -1

    async def calculate_real_gdp(self, nbs_id: int):
        start_time = time.time()
        log = {"req": "calculate_real_gdp", "start_time": start_time, "consumption": 0}
        request = org_service.CalculateRealGDPRequest(nbs_agent_id=nbs_id)
        response: org_service.CalculateRealGDPResponse = (
            await self._aio_stub.CalculateRealGDP(request)
        )
        log["consumption"] = time.time() - start_time
        self._log_list.append(log)
        return response.real_gdp

    async def calculate_interest(self, org_id: int, agent_ids: list[int]):
        """
        Calculate interest for agents based on their accounts.

        - **Args**:
            - `org_id` (`int`): The ID of the bank.
            - `agent_ids` (`List[int]`): A list of IDs for the agents whose interests are being calculated.

        - **Returns**:
            - `Tuple[float, List[float]]`: A tuple containing the total interest and updated currencies for each agent.
        """
        start_time = time.time()
        log = {"req": "calculate_interest", "start_time": start_time, "consumption": 0}
        request = org_service.CalculateInterestRequest(
            bank_id=org_id,
            agent_ids=agent_ids,
        )
        response: org_service.CalculateInterestResponse = (
            await self._aio_stub.CalculateInterest(request)
        )
        log["consumption"] = time.time() - start_time
        self._log_list.append(log)
        return (float(response.total_interest), list(response.updated_currencies))

    async def remove_agents(self, agent_ids: Union[int, list[int]]):
        """
        Remove one or more agents from the system.

        - **Args**:
            - `org_ids` (`Union[int, List[int]]`): A single ID or a list of IDs for the agents to be removed.
        """
        start_time = time.time()
        log = {"req": "remove_agents", "start_time": start_time, "consumption": 0}
        if isinstance(agent_ids, int):
            agent_ids = [agent_ids]
        tasks = [
            self._aio_stub.RemoveAgent(
                org_service.RemoveAgentRequest(agent_id=agent_id)
            )
            for agent_id in agent_ids
        ]
        await asyncio.gather(*tasks)
        log["consumption"] = time.time() - start_time
        self._log_list.append(log)

    async def remove_orgs(self, org_ids: Union[int, list[int]]):
        """
        Remove one or more organizations from the system.

        - **Args**:
            - `org_ids` (`Union[int, List[int]]`): A single ID or a list of IDs for the organizations to be removed.
        """
        start_time = time.time()
        log = {"req": "remove_orgs", "start_time": start_time, "consumption": 0}
        if isinstance(org_ids, int):
            org_ids = [org_ids]
        tasks = [
            self._aio_stub.RemoveOrg(org_service.RemoveOrgRequest(org_id=org_id))
            for org_id in org_ids
        ]
        await asyncio.gather(*tasks)
        log["consumption"] = time.time() - start_time
        self._log_list.append(log)

    async def save(self, file_path: str) -> tuple[list[int], list[int]]:
        """
        Save the current state of all economy entities to a specified file.

        - **Args**:
            - `file_path` (`str`): The path to the file where the economy entities will be saved.

        - **Returns**:
            - `Tuple[List[int], List[int]]`: A tuple containing lists of agent IDs and organization IDs that were saved.
        """
        start_time = time.time()
        log = {"req": "save", "start_time": start_time, "consumption": 0}
        request = org_service.SaveEconomyEntitiesRequest(
            file_path=file_path,
        )
        response: org_service.SaveEconomyEntitiesResponse = (
            await self._aio_stub.SaveEconomyEntities(request)
        )
        # current agent ids and org ids
        log["consumption"] = time.time() - start_time
        self._log_list.append(log)
        return (list(response.agent_ids), list(response.org_ids))

    async def load(self, file_path: str):
        """
        Load the state of economy entities from a specified file.

        - **Args**:
            - `file_path` (`str`): The path to the file from which the economy entities will be loaded.

        - **Returns**:
            - `Tuple[List[int], List[int]]`: A tuple containing lists of agent IDs and organization IDs that were loaded.
        """
        start_time = time.time()
        log = {"req": "load", "start_time": start_time, "consumption": 0}
        request = org_service.LoadEconomyEntitiesRequest(
            file_path=file_path,
        )
        response: org_service.LoadEconomyEntitiesResponse = (
            await self._aio_stub.LoadEconomyEntities(request)
        )
        # current agent ids and org ids
        log["consumption"] = time.time() - start_time
        self._log_list.append(log)
        return (list(response.agent_ids), list(response.org_ids))

    async def get_org_entity_ids(self, org_type: economyv2.OrgType) -> list[int]:
        """
        Get the IDs of all organizations of a specific type.

        - **Args**:
            - `org_type` (`economyv2.OrgType`): The type of organizations whose IDs are to be retrieved.

        - **Returns**:
            - `List[int]`: A list of organization IDs matching the specified type.
        """
        start_time = time.time()
        log = {"req": "get_org_entity_ids", "start_time": start_time, "consumption": 0}
        request = org_service.GetOrgEntityIdsRequest(
            type=org_type,
        )
        response: org_service.GetOrgEntityIdsResponse = (
            await self._aio_stub.GetOrgEntityIds(request)
        )
        log["consumption"] = time.time() - start_time
        self._log_list.append(log)
        return list(response.org_ids)

    async def add_delta_value(
        self,
        id: Union[int, list[int]],
        key: str,
        value: Any,
    ) -> Any:
        """
        Add value pair

        - **Args**:
            - `id` (`int`): The id of `Org` or `Agent`.
            - `key` (`str`): The attribute to update. Can only be `inventory`, `price`, `interest_rate` and `currency`

        - **Returns**:
            - Any
        """
        start_time = time.time()
        log = {"req": "add_delta_value", "start_time": start_time, "consumption": 0}
        pascal_key = ''.join(x.title() for x in key.split('_'))
        _request_type = getattr(org_service, f"Add{pascal_key}Request")
        _request_func = getattr(self._aio_stub, f"Add{pascal_key}")

        _available_keys = {"inventory", "price", "interest_rate", "currency", "income"}
        if key not in _available_keys:
            raise ValueError(f"Invalid key `{key}`, can only be {_available_keys}!")
        response = await _request_func(
            _request_type(
                **{
                    "org_id": id,
                    f"delta_{key}": value,
                }
            )
        )
        log["consumption"] = time.time() - start_time
        self._log_list.append(log)
        return response
