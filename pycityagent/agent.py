"""智能体模板类及其定义"""

from abc import ABC, abstractmethod
import asyncio
import json
from uuid import UUID
from copy import deepcopy
from datetime import datetime
import time
from enum import Enum
import logging
import random
import uuid
from typing import Dict, List, Optional

from pycityagent.environment.sim.person_service import PersonService
from mosstool.util.format_converter import dict2pb
from pycityproto.city.person.v2 import person_pb2 as person_pb2

from pycityagent.message.messager import Messager

from .economy import EconomyClient
from .environment import Simulator
from .llm import LLM
from .memory import Memory


class AgentType(Enum):
    """
    Agent类型

    - Citizen, Citizen type agent
    - Institution, Orgnization or institution type agent
    """

    Unspecified = "Unspecified"
    Citizen = "Citizen"
    Institution = "Institution"


class Agent(ABC):
    """
    Agent base class
    """

    def __init__(
        self,
        name: str,
        type: AgentType = AgentType.Unspecified,
        llm_client: Optional[LLM] = None,
        economy_client: Optional[EconomyClient] = None,
        messager: Optional[Messager] = None,
        simulator: Optional[Simulator] = None,
        memory: Optional[Memory] = None,
    ) -> None:
        """
        Initialize the Agent.

        Args:
            name (str): The name of the agent.
            type (AgentType): The type of the agent. Defaults to `AgentType.Unspecified`
            llm_client (LLM): The language model client. Defaults to None.
            economy_client (EconomyClient): The `EconomySim` client. Defaults to None.
            messager (Messager, optional): The messager object. Defaults to None.
            simulator (Simulator, optional): The simulator object. Defaults to None.
            memory (Memory, optional): The memory of the agent. Defaults to None.
        """
        self._name = name
        self._type = type
        self._uuid = uuid.uuid4()
        self._llm_client = llm_client
        self._economy_client = economy_client
        self._messager = messager
        self._simulator = simulator
        self._memory = memory
        self._exp_id = -1
        self._has_bound_to_simulator = False
        self._has_bound_to_economy = False
        self._blocked = False
        self._interview_history: List[Dict] = []  # 存储采访历史
        self._person_template = PersonService.default_dict_person()

    def __getstate__(self):
        state = self.__dict__.copy()
        # 排除锁对象
        del state["_llm_client"]
        return state

    def set_messager(self, messager: Messager):
        """
        Set the messager of the agent.
        """
        self._messager = messager

    def set_llm_client(self, llm_client: LLM):
        """
        Set the llm_client of the agent.
        """
        self._llm_client = llm_client

    def set_simulator(self, simulator: Simulator):
        """
        Set the simulator of the agent.
        """
        self._simulator = simulator

    def set_economy_client(self, economy_client: EconomyClient):
        """
        Set the economy_client of the agent.
        """
        self._economy_client = economy_client

    def set_memory(self, memory: Memory):
        """
        Set the memory of the agent.
        """
        self._memory = memory

    def set_exp_id(self, exp_id: str|UUID):
        """
        Set the exp_id of the agent.
        """
        self._exp_id = exp_id

    @property
    def uuid(self):
        """The Agent's UUID"""
        return self._uuid

    @property
    def sim_id(self):
        """The Agent's Simulator ID"""
        return self._agent_id

    @property
    def llm(self):
        """The Agent's LLM"""
        if self._llm_client is None:
            raise RuntimeError(
                f"LLM access before assignment, please `set_llm_client` first!"
            )
        return self._llm_client

    @property
    def economy_client(self):
        """The Agent's EconomyClient"""
        if self._economy_client is None:
            raise RuntimeError(
                f"EconomyClient access before assignment, please `set_economy_client` first!"
            )
        return self._economy_client

    @property
    def memory(self):
        """The Agent's Memory"""
        if self._memory is None:
            raise RuntimeError(
                f"Memory access before assignment, please `set_memory` first!"
            )
        return self._memory

    @property
    def simulator(self):
        """The Simulator"""
        if self._simulator is None:
            raise RuntimeError(
                f"Simulator access before assignment, please `set_simulator` first!"
            )
        return self._simulator

    async def generate_response(self, question: str) -> str:
        """生成回答

        基于智能体的记忆和当前状态，生成对问题的回答。

        Args:
            question: 需要回答的问题

        Returns:
            str: 智能体的回答
        """
        dialog = []

        # 添加系统提示
        system_prompt = f"请以第一人称的方式回答问题,保持回答简洁明了。"
        dialog.append({"role": "system", "content": system_prompt})

        # 添加记忆上下文
        if self._memory:
            relevant_memories = await self._memory.search(question)
            if relevant_memories:
                dialog.append(
                    {
                        "role": "system",
                        "content": f"基于以下记忆回答问题:\n{relevant_memories}",
                    }
                )

        # 添加用户问题
        dialog.append({"role": "user", "content": question})

        # 使用LLM生成回答
        if not self._llm_client:
            return "抱歉，我现在无法回答问题。"

        response = await self._llm_client.atext_request(dialog)  # type:ignore

        # 记录采访历史
        self._interview_history.append(
            {
                "timestamp": datetime.now().isoformat(),
                "question": question,
                "response": response,
            }
        )

        return response  # type:ignore

    def get_interview_history(self) -> List[Dict]:
        """获取采访历史记录"""
        return self._interview_history

    async def handle_agent_chat_message(self, payload: dict):
        """处理收到的消息，识别发送者"""
        # 从消息中解析发送者 ID 和消息内容
        print(
            f"Agent {self._uuid} received agent chat message: '{payload['content']}' from Agent {payload['from']}"
        )

    async def handle_user_chat_message(self, payload: dict):
        """处理收到的消息，识别发送者"""
        # 从消息中解析发送者 ID 和消息内容
        print(
            f"Agent {self._uuid} received user chat message: '{payload['content']}' from User"
        )

    async def handle_user_survey_message(self, payload: dict):
        """处理收到的消息，识别发送者"""
        # 从消息中解析发送者 ID 和消息内容
        print(
            f"Agent {self._uuid} received user survey message: '{payload['content']}' from User"
        )

    async def _send_message(
        self, to_agent_uuid: UUID, payload: dict, sub_topic: str
    ):
        """通过 Messager 发送消息"""
        if self._messager is None:
            raise RuntimeError("Messager is not set")
        topic = f"exps/{self._exp_id}/agents/{to_agent_uuid}/{sub_topic}"
        await self._messager.send_message(topic, payload)

    async def send_message_to_agent(
        self, to_agent_uuid: UUID, content: dict
    ):
        """通过 Messager 发送消息"""
        if self._messager is None:
            raise RuntimeError("Messager is not set")
        payload = {
            "from": self._uuid,
            "content": content,
            "timestamp": int(time.time()),
            "day": await self._simulator.get_simulator_day(),
            "t": await self._simulator.get_simulator_second_from_start_of_day(),
        }
        await self._send_message(to_agent_uuid, payload, "agent-chat")

    async def send_message_to_user(
        self, content: dict
    ):
        pass

    async def send_message_to_survey(
        self, content: dict
    ):
        pass

    @abstractmethod
    async def forward(self) -> None:
        """智能体行为逻辑"""
        raise NotImplementedError
    
    async def handle_gather_message(self, payload: str):
        raise NotImplementedError

    async def run(self) -> None:
        """
        统一的Agent执行入口
        当_blocked为True时，不执行forward方法
        """
        if not self._blocked:
            await self.forward()


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
        messager: Optional[Messager] = None,
    ) -> None:
        super().__init__(
            name,
            AgentType.Citizen,
            llm_client,
            economy_client,
            messager,
            simulator,
            memory,
        )

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
            logging.warning("Simulator is not set")
            return
        if not self._has_bound_to_simulator:
            FROM_MEMORY_KEYS = {
                "attribute",
                "home",
                "work",
                "vehicle_attribute",
                "bus_attribute",
                "pedestrian_attribute",
                "bike_attribute",
            }
            simulator = self._simulator
            memory = self._memory
            person_id = await memory.get("id")
            # ATTENTION:模拟器分配的id从0开始
            if person_id >= 0:
                await simulator.get_person(person_id)
                logging.debug(f"Binding to Person `{person_id}` already in Simulator")
            else:
                dict_person = deepcopy(self._person_template)
                for _key in FROM_MEMORY_KEYS:
                    try:
                        _value = await memory.get(_key)
                        if _value:
                            dict_person[_key] = _value
                    except KeyError as e:
                        continue
                resp = await simulator.add_person(
                    dict2pb(dict_person, person_pb2.Person())
                )
                person_id = resp["person_id"]
                await memory.update("id", person_id, protect_llm_read_only_fields=False)
                logging.debug(
                    f"Binding to Person `{person_id}` just added to Simulator"
                )
                # 防止模拟器还没有到prepare阶段导致get_person出错
            self._has_bound_to_simulator = True
            self._agent_id = person_id

    async def _bind_to_economy(self):
        if self._economy_client is None:
            logging.warning("Economy client is not set")
            return
        if not self._has_bound_to_economy:
            if self._has_bound_to_simulator:
                try:
                    await self._economy_client.remove_agents([self._agent_id])
                except:
                    pass
                person_id = await self._memory.get("id")
                await self._economy_client.add_agents(
                    {
                        "id": person_id,
                        "currency": await self._memory.get("currency"),
                    }
                )
                self._has_bound_to_economy = True
            else:
                logging.debug(
                    f"Binding to Economy before binding to Simulator, skip binding to Economy Simulator"
                )

    async def handle_gather_message(self, payload: dict):
        """处理收到的消息，识别发送者"""
        # 从消息中解析发送者 ID 和消息内容
        target = payload["target"]
        sender_id = payload["from"]
        content = await self.memory.get(f"{target}")
        payload = {
            "from": self._uuid,
            "content": content,
        }
        await self._send_message(sender_id, payload, "gather")


class InstitutionAgent(Agent):
    """
    InstitutionAgent: 机构智能体类及其定义
    """

    def __init__(
        self,
        name: str,
        llm_client: Optional[LLM] = None,
        simulator: Optional[Simulator] = None,
        memory: Optional[Memory] = None,
        economy_client: Optional[EconomyClient] = None,
        messager: Optional[Messager] = None,
    ) -> None:
        super().__init__(
            name,
            AgentType.Institution,
            llm_client,
            economy_client,
            messager,
            simulator,
            memory,
        )

    async def bind_to_simulator(self):
        await self._bind_to_economy()

    async def _bind_to_economy(self):
        if self._economy_client is None:
            logging.debug("Economy client is not set")
            return
        if not self._has_bound_to_economy:
            # TODO: More general id generation
            _id = random.randint(100000, 999999)
            self._agent_id = _id
            await self._memory.update("id", _id, protect_llm_read_only_fields=False)
            try:
                await self._economy_client.remove_orgs([self._agent_id])
            except:
                pass
            try:
                id = await self._memory.get("id")
                type = await self._memory.get("type")
                try:
                    nominal_gdp = await self._memory.get("nominal_gdp")
                except:
                    nominal_gdp = []
                try:
                    real_gdp = await self._memory.get("real_gdp")
                except:
                    real_gdp = []
                try:
                    unemployment = await self._memory.get("unemployment")
                except:
                    unemployment = []
                try:
                    wages = await self._memory.get("wages")
                except:
                    wages = []
                try:
                    prices = await self._memory.get("prices")
                except:
                    prices = []
                try:
                    inventory = await self._memory.get("inventory")
                except:
                    inventory = 0
                try:
                    price = await self._memory.get("price")
                except:
                    price = 0
                try:
                    currency = await self._memory.get("currency")
                except:
                    currency = 0.0
                try:
                    interest_rate = await self._memory.get("interest_rate")
                except:
                    interest_rate = 0.0
                try:
                    bracket_cutoffs = await self._memory.get("bracket_cutoffs")
                except:
                    bracket_cutoffs = []
                try:
                    bracket_rates = await self._memory.get("bracket_rates")
                except:
                    bracket_rates = []
                await self._economy_client.add_orgs(
                    {
                        "id": id,
                        "type": type,
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
                logging.error(f"Failed to bind to Economy: {e}")
            self._has_bound_to_economy = True

    async def handle_gather_message(self, payload: dict):
        """处理收到的消息，识别发送者"""
        # 从消息中解析发送者 ID 和消息内容
        content = payload["content"]
        sender_id = payload["from"]
        print(
            f"Agent {self._uuid} received gather message: '{content}' from Agent {sender_id}"
        )

    async def gather_messages(self, agent_ids: list[UUID], target: str):
        """从多个智能体收集消息"""
        payload = {
            "from": self._uuid,
            "target": target,
        }
        for agent_id in agent_ids:
            await self._send_message(agent_id, payload, "gather")
