from __future__ import annotations

import asyncio
import logging
import random
from copy import deepcopy
from typing import Any, Optional

from mosstool.util.format_converter import dict2pb
from pycityproto.city.person.v2 import person_pb2 as person_pb2

from ..economy import EconomyClient
from ..environment import Simulator
from ..llm import LLM
from ..memory import Memory
from ..message import MessageInterceptor, Messager
from ..metrics import MlflowClient
from .agent_base import Agent, AgentType

logger = logging.getLogger("pycityagent")


class CitizenAgent(Agent):
    """
    CitizenAgent: 城市居民智能体类及其定义
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
        await self._bind_to_simulator()
        await self._bind_to_economy()

    async def _bind_to_simulator(self):
        """
        Bind Agent to Simulator

        Args:
            person_template (dict, optional): The person template in dict format. Defaults to PersonService.default_dict_person().
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
        resp = await simulator.add_person(dict2pb(dict_person, person_pb2.Person()))
        person_id = resp["person_id"]
        await status.update("id", person_id, protect_llm_read_only_fields=False)
        logger.debug(f"Binding to Person `{person_id}` just added to Simulator")
        self._agent_id = person_id
        self.status.set_agent_id(person_id)

    async def _bind_to_economy(self):
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
            await self._economy_client.add_agents(
                {
                    "id": person_id,
                    "currency": currency,
                }
            )
            self._has_bound_to_economy = True

    async def handle_gather_message(self, payload: dict):
        """处理收到的消息，识别发送者"""
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
    InstitutionAgent: Institution agent class and definition
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
        await self._bind_to_economy()

    async def _bind_to_economy(self):
        if self._economy_client is None:
            logger.debug("Economy client is not set")
            return
        if not self._has_bound_to_economy:
            # TODO: More general id generation
            _id = random.randint(100000, 999999)
            self._agent_id = _id
            self.status.set_agent_id(_id)
            map_header = self.simulator.map.header
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
                try:
                    nominal_gdp = await _status.get("nominal_gdp")
                except:
                    nominal_gdp = []
                try:
                    real_gdp = await _status.get("real_gdp")
                except:
                    real_gdp = []
                try:
                    unemployment = await _status.get("unemployment")
                except:
                    unemployment = []
                try:
                    wages = await _status.get("wages")
                except:
                    wages = []
                try:
                    prices = await _status.get("prices")
                except:
                    prices = []
                try:
                    inventory = await _status.get("inventory")
                except:
                    inventory = 0
                try:
                    price = await _status.get("price")
                except:
                    price = 0
                try:
                    currency = await _status.get("currency")
                except:
                    currency = 0.0
                try:
                    interest_rate = await _status.get("interest_rate")
                except:
                    interest_rate = 0.0
                try:
                    bracket_cutoffs = await _status.get("bracket_cutoffs")
                except:
                    bracket_cutoffs = []
                try:
                    bracket_rates = await _status.get("bracket_rates")
                except:
                    bracket_rates = []
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
                    }
                )
            except Exception as e:
                logger.error(f"Failed to bind to Economy: {e}")
            self._has_bound_to_economy = True

    async def handle_gather_message(self, payload: dict):
        """处理收到的消息，识别发送者"""
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
        """从多个智能体收集消息

        Args:
            agent_uuids: 目标智能体UUID列表
            target: 要收集的信息类型

        Returns:
            list[dict]: 收集到的所有响应
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
