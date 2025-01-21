import asyncio
import logging
from typing import Any, Literal, Union

import grpc
import pycityproto.city.economy.v2.economy_pb2 as economyv2
import pycityproto.city.economy.v2.org_service_pb2 as org_service
import pycityproto.city.economy.v2.org_service_pb2_grpc as org_grpc
from google.protobuf import descriptor

__all__ = [
    "EconomyClient",
]


def _snake_to_pascal(snake_str):
    _res = "".join(word.capitalize() or "_" for word in snake_str.split("_"))
    for _word in {
        "Gdp",
    }:
        if _word in _res:
            _res = _res.replace(_word, _word.upper())
    return _res


def _get_field_type_and_repeated(message, field_name: str) -> tuple[Any, bool]:
    try:
        field_descriptor = message.DESCRIPTOR.fields_by_name[field_name]
        field_type = field_descriptor.type
        _type_mapping = {
            descriptor.FieldDescriptor.TYPE_FLOAT: float,
            descriptor.FieldDescriptor.TYPE_INT32: int,
        }
        is_repeated = (
            field_descriptor.label == descriptor.FieldDescriptor.LABEL_REPEATED
        )
        return (_type_mapping.get(field_type), is_repeated)
    except KeyError:
        raise KeyError(f"Invalid message {message} and filed name {field_name}!")


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

    def __init__(self, server_address: str, secure: bool = False):
        """
        Initialize the EconomyClient.

        - **Args**:
            - `server_address` (`str`): The address of the Economy server to connect to.
            - `secure` (`bool`, optional): Whether to use a secure connection. Defaults to `False`.

        - **Attributes**:
            - `server_address` (`str`): The address of the Economy server.
            - `secure` (`bool`): A flag indicating if a secure connection should be used.
            - `_aio_stub` (`OrgServiceStub`): A gRPC stub used to make remote calls to the Economy service.

        - **Description**:
            - Initializes the EconomyClient with the specified server address and security preference.
            - Creates an asynchronous gRPC channel using `_create_aio_channel`.
            - Instantiates a gRPC stub (`_aio_stub`) for interacting with the Economy service.
        """
        self.server_address = server_address
        self.secure = secure
        aio_channel = _create_aio_channel(server_address, secure)
        self._aio_stub = org_grpc.OrgServiceStub(aio_channel)

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
        """ "
        Restore instance attributes (i.e., filename and mode) from the
        unpickled state dictionary.
        """
        self.__dict__.update(state)
        # Re-initialize the channel after unpickling
        aio_channel = _create_aio_channel(self.server_address, self.secure)
        self._aio_stub = org_grpc.OrgServiceStub(aio_channel)

    async def get(
        self,
        id: int,
        key: str,
    ) -> Any:
        """
        Get specific value

        - **Args**:
            - `id` (`int`): The id of `Org` or `Agent`.
            - `key` (`str`): The attribute to fetch.

        - **Returns**:
            - Any
        """
        pascal_key = _snake_to_pascal(key)
        _request_type = getattr(org_service, f"Get{pascal_key}Request")
        _request_func = getattr(self._aio_stub, f"Get{pascal_key}")
        response = await _request_func(_request_type(org_id=id))
        value_type, is_repeated = _get_field_type_and_repeated(response, field_name=key)
        if is_repeated:
            return list(getattr(response, key))
        else:
            return value_type(getattr(response, key))

    async def update(
        self,
        id: int,
        key: str,
        value: Any,
        mode: Union[Literal["replace"], Literal["merge"]] = "replace",
    ) -> Any:
        """
        Update key-value pair

        - **Args**:
            - `id` (`int`): The id of `Org` or `Agent`.
            - `key` (`str`): The attribute to update.
            - `mode` (Union[Literal["replace"], Literal["merge"]], optional): Update mode. Defaults to "replace".


        - **Returns**:
            - Any
        """
        pascal_key = _snake_to_pascal(key)
        _request_type = getattr(org_service, f"Set{pascal_key}Request")
        _request_func = getattr(self._aio_stub, f"Set{pascal_key}")
        if mode == "merge":
            orig_value = await self.get(id, key)
            _orig_type = type(orig_value)
            _new_type = type(value)
            if _orig_type != _new_type:
                logging.debug(
                    f"Inconsistent type of original value {_orig_type.__name__} and to-update value {_new_type.__name__}"
                )
            else:
                if isinstance(orig_value, set):
                    orig_value.update(set(value))
                    value = orig_value
                elif isinstance(orig_value, dict):
                    orig_value.update(dict(value))
                    value = orig_value
                elif isinstance(orig_value, list):
                    orig_value.extend(list(value))
                    value = orig_value
                else:
                    logging.warning(
                        f"Type of {type(orig_value)} does not support mode `merge`, using `replace` instead!"
                    )
        return await _request_func(
            _request_type(
                **{
                    "org_id": id,
                    key: value,
                }
            )
        )

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
        if isinstance(configs, dict):
            configs = [configs]
        tasks = [
            self._aio_stub.AddAgent(
                org_service.AddAgentRequest(
                    agent=economyv2.Agent(
                        id=config["id"],
                        currency=config.get("currency", 0.0),
                    )
                )
            )
            for config in configs
        ]
        responses = await asyncio.gather(*tasks)

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
        if isinstance(configs, dict):
            configs = [configs]
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
                    )
                )
            )
            for config in configs
        ]
        responses = await asyncio.gather(*tasks)

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
        request = org_service.CalculateTaxesDueRequest(
            government_id=org_id,
            agent_ids=agent_ids,
            incomes=incomes,
            enable_redistribution=enable_redistribution,
        )
        response: org_service.CalculateTaxesDueResponse = (
            await self._aio_stub.CalculateTaxesDue(request)
        )
        return (float(response.taxes_due), list(response.updated_incomes))

    async def calculate_consumption(
        self, org_id: int, agent_ids: list[int], demands: list[int]
    ):
        """
        Calculate consumption for agents based on their demands.

        - **Args**:
            - `org_id` (`int`): The ID of the firm providing goods or services.
            - `agent_ids` (`List[int]`): A list of IDs for the agents whose consumption is being calculated.
            - `demands` (`List[int]`): A list of demand quantities corresponding to each agent.

        - **Returns**:
            - `Tuple[int, List[float]]`: A tuple containing the remaining inventory and updated currencies for each agent.
        """
        request = org_service.CalculateConsumptionRequest(
            firm_id=org_id,
            agent_ids=agent_ids,
            demands=demands,
        )
        response: org_service.CalculateConsumptionResponse = (
            await self._aio_stub.CalculateConsumption(request)
        )
        return (int(response.remain_inventory), list(response.updated_currencies))

    async def calculate_interest(self, org_id: int, agent_ids: list[int]):
        """
        Calculate interest for agents based on their accounts.

        - **Args**:
            - `org_id` (`int`): The ID of the bank.
            - `agent_ids` (`List[int]`): A list of IDs for the agents whose interests are being calculated.

        - **Returns**:
            - `Tuple[float, List[float]]`: A tuple containing the total interest and updated currencies for each agent.
        """
        request = org_service.CalculateInterestRequest(
            bank_id=org_id,
            agent_ids=agent_ids,
        )
        response: org_service.CalculateInterestResponse = (
            await self._aio_stub.CalculateInterest(request)
        )
        return (float(response.total_interest), list(response.updated_currencies))

    async def remove_agents(self, agent_ids: Union[int, list[int]]):
        """
        Remove one or more agents from the system.

        - **Args**:
            - `org_ids` (`Union[int, List[int]]`): A single ID or a list of IDs for the agents to be removed.
        """
        if isinstance(agent_ids, int):
            agent_ids = [agent_ids]
        tasks = [
            self._aio_stub.RemoveAgent(
                org_service.RemoveAgentRequest(agent_id=agent_id)
            )
            for agent_id in agent_ids
        ]
        responses = await asyncio.gather(*tasks)

    async def remove_orgs(self, org_ids: Union[int, list[int]]):
        """
        Remove one or more organizations from the system.

        - **Args**:
            - `org_ids` (`Union[int, List[int]]`): A single ID or a list of IDs for the organizations to be removed.
        """
        if isinstance(org_ids, int):
            org_ids = [org_ids]
        tasks = [
            self._aio_stub.RemoveOrg(org_service.RemoveOrgRequest(org_id=org_id))
            for org_id in org_ids
        ]
        responses = await asyncio.gather(*tasks)

    async def save(self, file_path: str) -> tuple[list[int], list[int]]:
        """
        Save the current state of all economy entities to a specified file.

        - **Args**:
            - `file_path` (`str`): The path to the file where the economy entities will be saved.

        - **Returns**:
            - `Tuple[List[int], List[int]]`: A tuple containing lists of agent IDs and organization IDs that were saved.
        """
        request = org_service.SaveEconomyEntitiesRequest(
            file_path=file_path,
        )
        response: org_service.SaveEconomyEntitiesResponse = (
            await self._aio_stub.SaveEconomyEntities(request)
        )
        # current agent ids and org ids
        return (list(response.agent_ids), list(response.org_ids))

    async def load(self, file_path: str):
        """
        Load the state of economy entities from a specified file.

        - **Args**:
            - `file_path` (`str`): The path to the file from which the economy entities will be loaded.

        - **Returns**:
            - `Tuple[List[int], List[int]]`: A tuple containing lists of agent IDs and organization IDs that were loaded.
        """
        request = org_service.LoadEconomyEntitiesRequest(
            file_path=file_path,
        )
        response: org_service.LoadEconomyEntitiesResponse = (
            await self._aio_stub.LoadEconomyEntities(request)
        )
        # current agent ids and org ids
        return (list(response.agent_ids), list(response.org_ids))

    async def get_org_entity_ids(self, org_type: economyv2.OrgType) -> list[int]:
        """
        Get the IDs of all organizations of a specific type.

        - **Args**:
            - `org_type` (`economyv2.OrgType`): The type of organizations whose IDs are to be retrieved.

        - **Returns**:
            - `List[int]`: A list of organization IDs matching the specified type.
        """
        request = org_service.GetOrgEntityIdsRequest(
            type=org_type,
        )
        response: org_service.GetOrgEntityIdsResponse = (
            await self._aio_stub.GetOrgEntityIds(request)
        )
        return list(response.org_ids)

    async def add_delta_value(
        self,
        id: int,
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
        pascal_key = _snake_to_pascal(key)
        _request_type = getattr(org_service, f"Add{pascal_key}Request")
        _request_func = getattr(self._aio_stub, f"Add{pascal_key}")
        _available_keys = {
            "inventory",
            "price",
            "interest_rate",
            "currency",
        }
        if key not in _available_keys:
            raise ValueError(f"Invalid key `{key}`, can only be {_available_keys}!")
        return await _request_func(
            _request_type(
                **{
                    "org_id": id,
                    f"delta_{key}": value,
                }
            )
        )
