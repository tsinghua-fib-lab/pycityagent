from __future__ import annotations

import asyncio
import logging
import random
from copy import deepcopy
from typing import Any, Optional

import ray
from pycityproto.city.person.v2 import person_pb2 as person_pb2

from ..environment import EconomyClient, Simulator
from ..llm import LLM
from ..memory import Memory
from ..message import MessageInterceptor, Messager
from ..metrics import MlflowClient
from .agent_base import Agent, AgentType

logger = logging.getLogger("agentsociety")

__all__ = [
    "InstitutionAgent",
    "CitizenAgent",
]


class CitizenAgent(Agent):
    """
    Represents a citizen agent within the simulation environment.

    - **Description**:
        - This class extends the base `Agent` class and is designed to simulate the behavior of a city resident.
        - It includes initialization of various clients (like LLM, economy) and services required for the agent's operation.
        - Provides methods for binding the agent to the simulator and economy system, as well as handling specific types of messages.

    - **Attributes**:
        - `_mlflow_client`: An optional client for integrating with MLflow for experiment tracking and management.
    """

    def __init__(
        self,
        name: str,
        llm_client: Optional[LLM] = None,
        simulator: Optional[Simulator] = None,
        memory: Optional[Memory] = None,
        economy_client: Optional[EconomyClient] = None,
        messager: Optional[Messager] = None,  # type:ignore
        message_interceptor: Optional[MessageInterceptor] = None,  # type:ignore
        avro_file: Optional[dict] = None,
    ) -> None:
        """
        Initialize a new instance of the CitizenAgent.

        - **Args**:
            - `name` (`str`): The name or identifier of the agent.
            - `llm_client` (`Optional[LLM]`, optional): A client for interacting with a Language Model. Defaults to `None`.
            - `simulator` (`Optional[Simulator]`, optional): A reference to the simulation environment. Defaults to `None`.
            - `memory` (`Optional[Memory]`, optional): A memory storage object for the agent. Defaults to `None`.
            - `economy_client` (`Optional[EconomyClient]`, optional): A client for managing economic transactions. Defaults to `None`.
            - `messager` (`Optional[Messager]`, optional): A communication service for messaging between agents. Defaults to `None`.
            - `message_interceptor` (`Optional[MessageInterceptor]`, optional): An interceptor for modifying messages before they are processed. Defaults to `None`.
            - `avro_file` (`Optional[dict]`, optional): Configuration for writing data in Avro format. Defaults to `None`.

        - **Description**:
            - Initializes the CitizenAgent with the provided parameters and sets up necessary internal states.
        """
        super().__init__(
            name=name,
            type=AgentType.Citizen,
            llm_client=llm_client,
            economy_client=economy_client,
            messager=messager,
            message_interceptor=message_interceptor,
            simulator=simulator,
            memory=memory,
            avro_file=avro_file,
        )
        self._mlflow_client = None

    async def bind_to_simulator(self):
        """
        Bind the agent to both the Traffic Simulator and Economy Simulator.

        - **Description**:
            - Calls the `_bind_to_simulator` method to establish the agent within the simulation environment.
            - Calls the `_bind_to_economy` method to integrate the agent into the economy simulator.
        """
        await self._bind_to_simulator()
        await self._bind_to_economy()

    async def _bind_to_simulator(self):
        """
        Bind the agent to the Traffic Simulator.

        - **Description**:
            - If the simulator is set, this method binds the agent by creating a person entity in the simulator based on the agent's attributes.
            - Updates the agent's status with the newly created person ID from the simulator.
            - Logs the successful binding to the person entity added to the simulator.
        """
        if self._simulator is None:
            logger.warning("Simulator is not set")
            return
        FROM_MEMORY_KEYS = {
            "attribute",
            "home",
            "work",
            "vehicle_attribute",
            "bus_attribute",
            "pedestrian_attribute",
            "bike_attribute",
        }
        simulator = self.simulator
        status = self.status
        dict_person = deepcopy(self._person_template)
        for _key in FROM_MEMORY_KEYS:
            try:
                _value = await status.get(_key)
                if _value:
                    dict_person[_key] = _value
            except KeyError as e:
                continue
        resp = await simulator.add_person(dict_person)
        person_id = resp["person_id"]
        await status.update("id", person_id, protect_llm_read_only_fields=False)
        logger.debug(f"Binding to Person `{person_id}` just added to Simulator")
        self._agent_id = person_id
        self.status.set_agent_id(person_id)

    async def _bind_to_economy(self):
        """
        Bind the agent to the Economy Simulator.

        - **Description**:
            - If the economy client is set and the agent has not yet been bound to the economy, this method removes any existing agent with the same ID and adds the current agent to the economy.
            - Sets `_has_bound_to_economy` to `True` after successfully adding the agent.
        """
        if self._economy_client is None:
            logger.warning("Economy client is not set")
            return
        if not self._has_bound_to_economy:
            try:
                await self._economy_client.remove_agents([self._agent_id])
            except:
                pass
            person_id = await self.status.get("id")
            currency = await self.status.get("currency")
            skill = await self.status.get("work_skill")
            consumption = 0.0
            income = 0.0
            await self._economy_client.add_agents(
                {
                    "id": person_id,
                    "currency": currency,
                    "skill": skill,
                    "consumption": consumption,
                    "income": income,
                }
            )
            self._has_bound_to_economy = True

    async def handle_gather_message(self, payload: dict):
        """
        Handle a gather message received by the agent.

        - **Args**:
            - `payload` (`dict`): The message payload containing the target attribute and sender ID.

        - **Description**:
            - Extracts the target attribute and sender ID from the payload.
            - Retrieves the content associated with the target attribute from the agent's status.
            - Prepares a response payload with the retrieved content and sends it back to the sender using `_send_message`.
        """
        # 处理收到的消息，识别发送者
        # 从消息中解析发送者 ID 和消息内容
        target = payload["target"]
        sender_id = payload["from"]
        content = await self.status.get(f"{target}")
        payload = {
            "from": self._uuid,
            "content": content,
        }
        await self._send_message(sender_id, payload, "gather")

    @property
    def mlflow_client(self) -> MlflowClient:
        """The Agent's MlflowClient"""
        if self._mlflow_client is None:
            raise RuntimeError(
                f"MlflowClient access before assignment, please `set_mlflow_client` first!"
            )
        return self._mlflow_client

    def set_mlflow_client(self, mlflow_client: MlflowClient):
        """
        Set the mlflow_client of the agent.
        """
        self._mlflow_client = mlflow_client


class InstitutionAgent(Agent):
    """
    Represents an institution agent within the simulation environment.

    - **Description**:
        - This class extends the base `Agent` class and is designed to simulate the behavior of an institution, such as a bank, government body, or corporation.
        - It includes initialization of various clients (like LLM, economy) and services required for the agent's operation.
        - Provides methods for binding the agent to the economy system and handling specific types of messages, like gathering information from other agents.

    - **Attributes**:
        - `_mlflow_client`: An optional client for integrating with MLflow for experiment tracking and management.
        - `_gather_responses`: A dictionary mapping agent UUIDs to `asyncio.Future` objects used for collecting responses to gather requests.
    """

    def __init__(
        self,
        name: str,
        llm_client: Optional[LLM] = None,
        simulator: Optional[Simulator] = None,
        memory: Optional[Memory] = None,
        economy_client: Optional[EconomyClient] = None,
        messager: Optional[Messager] = None,  # type:ignore
        message_interceptor: Optional[MessageInterceptor] = None,  # type:ignore
        avro_file: Optional[dict] = None,
    ) -> None:
        """
        Initialize a new instance of the InstitutionAgent.

        - **Args**:
            - `name` (`str`): The name or identifier of the agent.
            - `llm_client` (`Optional[LLM]`, optional): A client for interacting with a Language Model. Defaults to `None`.
            - `simulator` (`Optional[Simulator]`, optional): A reference to the simulation environment. Defaults to `None`.
            - `memory` (`Optional[Memory]`, optional): A memory storage object for the agent. Defaults to `None`.
            - `economy_client` (`Optional[EconomyClient]`, optional): A client for managing economic transactions. Defaults to `None`.
            - `messager` (`Optional[Messager]`, optional): A communication service for messaging between agents. Defaults to `None`.
            - `message_interceptor` (`Optional[MessageInterceptor]`, optional): An interceptor for modifying messages before they are processed. Defaults to `None`.
            - `avro_file` (`Optional[dict]`, optional): Configuration for writing data in Avro format. Defaults to `None`.

        - **Description**:
            - Initializes the InstitutionAgent with the provided parameters and sets up necessary internal states.
            - Adds a response collector (`_gather_responses`) for handling responses to gather requests.
        """
        super().__init__(
            name=name,
            type=AgentType.Institution,
            llm_client=llm_client,
            economy_client=economy_client,
            messager=messager,
            message_interceptor=message_interceptor,
            simulator=simulator,
            memory=memory,
            avro_file=avro_file,
        )
        self._mlflow_client = None
        # 添加响应收集器
        self._gather_responses: dict[str, asyncio.Future] = {}

    async def bind_to_simulator(self):
        """
        Bind the agent to the Economy Simulator.

        - **Description**:
            - Calls the `_bind_to_economy` method to integrate the agent into the economy simulator.
        """
        await self._bind_to_economy()

    async def _bind_to_economy(self):
        """
        Bind the agent to the Economy Simulator.

        - **Description**:
            - Calls the `_bind_to_economy` method to integrate the agent into the economy system.
            - Note that this method does not bind the agent to the simulator itself; it only handles the economy integration.
        """
        if self._economy_client is None:
            logger.debug("Economy client is not set")
            return
        if not self._has_bound_to_economy:
            # TODO: More general id generation
            _id = random.randint(100000, 999999)
            self._agent_id = _id
            self.status.set_agent_id(_id)
            map_header: dict = ray.get(
                self.simulator.map.get_map_header.remote()  # type:ignore
            )
            # TODO: remove random position assignment
            await self.status.update(
                "position",
                {
                    "xy_position": {
                        "x": float(
                            random.randrange(
                                start=int(map_header["west"]),
                                stop=int(map_header["east"]),
                            )
                        ),
                        "y": float(
                            random.randrange(
                                start=int(map_header["south"]),
                                stop=int(map_header["north"]),
                            )
                        ),
                    }
                },
                protect_llm_read_only_fields=False,
            )
            await self.status.update("id", _id, protect_llm_read_only_fields=False)
            try:
                await self._economy_client.remove_orgs([self._agent_id])
            except:
                pass
            try:
                _status = self.status
                _id = await _status.get("id")
                _type = await _status.get("type")
                nominal_gdp = await _status.get("nominal_gdp", [])
                real_gdp = await _status.get("real_gdp", [])
                unemployment = await _status.get("unemployment", [])
                wages = await _status.get("wages", [])
                prices = await _status.get("prices", [])
                inventory = await _status.get("inventory", 0)
                price = await _status.get("price", 0)
                currency = await _status.get("currency", 0.0)
                interest_rate = await _status.get("interest_rate", 0.0)
                bracket_cutoffs = await _status.get("bracket_cutoffs", [])
                bracket_rates = await _status.get("bracket_rates", [])
                consumption_currency = await _status.get("consumption_currency", [])
                consumption_propensity = await _status.get("consumption_propensity", [])
                income_currency = await _status.get("income_currency", [])
                depression = await _status.get("depression", [])
                locus_control = await _status.get("locus_control", [])
                working_hours = await _status.get("working_hours", [])
                employees = await _status.get("employees", [])
                citizens = await _status.get("citizens", [])
                demand = await _status.get("demand", 0)
                sales = await _status.get("sales", 0)
                await self._economy_client.add_orgs(
                    {
                        "id": _id,
                        "type": _type,
                        "nominal_gdp": nominal_gdp,
                        "real_gdp": real_gdp,
                        "unemployment": unemployment,
                        "wages": wages,
                        "prices": prices,
                        "inventory": inventory,
                        "price": price,
                        "currency": currency,
                        "interest_rate": interest_rate,
                        "bracket_cutoffs": bracket_cutoffs,
                        "bracket_rates": bracket_rates,
                        "consumption_currency": consumption_currency,
                        "consumption_propensity": consumption_propensity,
                        "income_currency": income_currency,
                        "depression": depression,
                        "locus_control": locus_control,
                        "working_hours": working_hours,
                        "employees": employees,
                        "citizens": citizens,
                        "demand": demand,
                        "sales": sales,
                    }
                )
            except Exception as e:
                logger.error(f"Failed to bind to Economy: {e}")
            self._has_bound_to_economy = True

    async def handle_gather_message(self, payload: dict):
        """
        Handle a gather message received by the agent.

        - **Args**:
            - `payload` (`dict`): The message payload containing the content and sender ID.

        - **Description**:
            - Extracts the content and sender ID from the payload.
            - Stores the response in the corresponding Future object using the sender ID as the key.
        """
        content = payload["content"]
        sender_id = payload["from"]

        # 将响应存储到对应的Future中
        response_key = str(sender_id)
        if response_key in self._gather_responses:
            self._gather_responses[response_key].set_result(
                {
                    "from": sender_id,
                    "content": content,
                }
            )

    async def gather_messages(self, agent_uuids: list[str], target: str) -> list[dict]:
        """
        Gather messages from multiple agents.

        - **Args**:
            - `agent_uuids` (`list[str]`): A list of UUIDs for the target agents.
            - `target` (`str`): The type of information to collect from each agent.

        - **Returns**:
            - `list[dict]`: A list of dictionaries containing the collected responses.

        - **Description**:
            - For each agent UUID provided, creates a `Future` object to wait for its response.
            - Sends a gather request to each specified agent.
            - Waits for all responses and returns them as a list of dictionaries.
            - Ensures cleanup of Futures after collecting responses.
        """
        # 为每个agent创建Future
        futures = {}
        for agent_uuid in agent_uuids:
            futures[agent_uuid] = asyncio.Future()
            self._gather_responses[agent_uuid] = futures[agent_uuid]

        # 发送gather请求
        payload = {
            "from": self._uuid,
            "target": target,
        }
        for agent_uuid in agent_uuids:
            await self._send_message(agent_uuid, payload, "gather")

        try:
            # 等待所有响应
            responses = await asyncio.gather(*futures.values())
            return responses
        finally:
            # 清理Future
            for key in futures:
                self._gather_responses.pop(key, None)

    @property
    def mlflow_client(self) -> MlflowClient:
        """The Agent's MlflowClient"""
        if self._mlflow_client is None:
            raise RuntimeError(
                f"MlflowClient access before assignment, please `set_mlflow_client` first!"
            )
        return self._mlflow_client

    def set_mlflow_client(self, mlflow_client: MlflowClient):
        """
        Set the mlflow_client of the agent.
        """
        self._mlflow_client = mlflow_client
