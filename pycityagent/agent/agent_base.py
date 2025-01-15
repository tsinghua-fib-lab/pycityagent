from __future__ import annotations

import asyncio
import inspect
import json
import logging
import uuid
from abc import ABC, abstractmethod
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Optional, Union, get_type_hints

import fastavro
import ray
from pycityproto.city.person.v2 import person_pb2 as person_pb2

from ..economy import EconomyClient
from ..environment import Simulator
from ..environment.sim.person_service import PersonService
from ..llm import LLM
from ..memory import Memory
from ..message import MessageInterceptor, Messager
from ..metrics import MlflowClient
from ..utils import DIALOG_SCHEMA, SURVEY_SCHEMA, process_survey_for_llm
from ..workflow import Block

logger = logging.getLogger("pycityagent")


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

    configurable_fields: list[str] = []
    default_values: dict[str, Any] = {}
    fields_description: dict[str, str] = {}

    def __init__(
        self,
        name: str,
        type: AgentType = AgentType.Unspecified,
        llm_client: Optional[LLM] = None,
        economy_client: Optional[EconomyClient] = None,
        messager: Optional[ray.ObjectRef] = None,
        message_interceptor: Optional[ray.ObjectRef] = None,
        simulator: Optional[Simulator] = None,
        memory: Optional[Memory] = None,
        avro_file: Optional[dict[str, str]] = None,
        copy_writer: Optional[ray.ObjectRef] = None,
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
            avro_file (dict[str, str], optional): The avro file of the agent. Defaults to None.
            copy_writer (ray.ObjectRef): The copy_writer of the agent. Defaults to None.
        """
        self._name = name
        self._type = type
        self._uuid = str(uuid.uuid4())
        self._llm_client = llm_client
        self._economy_client = economy_client
        self._messager = messager
        self._message_interceptor = message_interceptor
        self._simulator = simulator
        self._memory = memory
        self._exp_id = -1
        self._agent_id = -1
        self._has_bound_to_simulator = False
        self._has_bound_to_economy = False
        self._blocked = False
        self._interview_history: list[dict] = []  # 存储采访历史
        self._person_template = PersonService.default_dict_person()
        self._avro_file = avro_file
        self._pgsql_writer = copy_writer
        self._last_asyncio_pg_task = None  # 将SQL写入的IO隐藏到计算任务后

    def __getstate__(self):
        state = self.__dict__.copy()
        # 排除锁对象
        del state["_llm_client"]
        return state

    @classmethod
    def export_class_config(cls) -> dict[str, dict]:
        result = {
            "agent_name": cls.__name__,
            "config": {},
            "description": {},
            "blocks": [],
        }
        config = {
            field: cls.default_values.get(field, "default_value")
            for field in cls.configurable_fields
        }
        result["config"] = config
        result["description"] = {
            field: cls.fields_description.get(field, "")
            for field in cls.configurable_fields
        }
        # 解析类中的注解，找到Block类型的字段
        hints = get_type_hints(cls)
        for attr_name, attr_type in hints.items():
            if inspect.isclass(attr_type) and issubclass(attr_type, Block):
                block_config = attr_type.export_class_config()
                result["blocks"].append(
                    {
                        "name": attr_name,
                        "config": block_config[0],  # type:ignore
                        "description": block_config[1],  # type:ignore
                        "children": cls._export_subblocks(attr_type),
                    }
                )
        return result

    @classmethod
    def _export_subblocks(cls, block_cls: type[Block]) -> list[dict]:
        children = []
        hints = get_type_hints(block_cls)  # 获取类的注解
        for attr_name, attr_type in hints.items():
            if inspect.isclass(attr_type) and issubclass(attr_type, Block):
                block_config = attr_type.export_class_config()
                children.append(
                    {
                        "name": attr_name,
                        "config": block_config[0],  # type:ignore
                        "description": block_config[1],  # type:ignore
                        "children": cls._export_subblocks(attr_type),
                    }
                )
        return children

    @classmethod
    def export_to_file(cls, filepath: str) -> None:
        config = cls.export_class_config()
        with open(filepath, "w") as f:
            json.dump(config, f, indent=4)

    @classmethod
    def import_block_config(cls, config: dict[str, Union[list[dict], str]]) -> Agent:
        agent = cls(name=config["agent_name"])  # type:ignore

        def build_block(block_data: dict[str, Any]) -> Block:
            block_cls = globals()[block_data["name"]]
            block_instance = block_cls.import_config(block_data)
            return block_instance

        # 创建顶层Block
        for block_data in config["blocks"]:
            assert isinstance(block_data, dict)
            block = build_block(block_data)
            setattr(agent, block.name.lower(), block)

        return agent

    @classmethod
    def import_from_file(cls, filepath: str) -> Agent:
        with open(filepath, "r") as f:
            config = json.load(f)
            return cls.import_block_config(config)

    def load_from_config(self, config: dict[str, list[dict]]) -> None:
        """
        使用配置更新当前Agent实例的Block层次结构。
        """
        # 更新当前Agent的基础参数
        for field in self.configurable_fields:
            if field in config["config"]:
                if config["config"][field] != "default_value":
                    setattr(self, field, config["config"][field])

        # 递归更新或创建顶层Block
        for block_data in config.get("blocks", []):
            block_name = block_data["name"]
            existing_block = getattr(self, block_name, None)  # type:ignore

            if existing_block:
                # 如果Block已经存在，则递归更新
                existing_block.load_from_config(block_data)
            else:
                raise KeyError(
                    f"Block '{block_name}' not found in agent '{self.__class__.__name__}'"
                )

    def load_from_file(self, filepath: str) -> None:
        with open(filepath, "r") as f:
            config = json.load(f)
            self.load_from_config(config)

    def set_messager(self, messager: Messager):  # type:ignore
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

    def set_exp_id(self, exp_id: str):
        """
        Set the exp_id of the agent.
        """
        self._exp_id = exp_id

    def set_avro_file(self, avro_file: dict[str, str]):
        """
        Set the avro file of the agent.
        """
        self._avro_file = avro_file

    def set_pgsql_writer(self, pgsql_writer: ray.ObjectRef):
        """
        Set the PostgreSQL copy writer of the agent.
        """
        self._pgsql_writer = pgsql_writer

    def set_message_interceptor(self, message_interceptor: ray.ObjectRef):
        """
        Set the PostgreSQL copy writer of the agent.
        """
        self._message_interceptor = message_interceptor

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
    def status(self):
        """The Agent's Status Memory"""
        if self.memory.status is None:
            raise RuntimeError(
                f"Status access before assignment, please `set_memory` first!"
            )
        return self.memory.status

    @property
    def stream(self):
        """The Agent's Stream Memory"""
        if self.memory.stream is None:
            raise RuntimeError(
                f"Stream access before assignment, please `set_memory` first!"
            )
        return self.memory.stream

    @property
    def simulator(self):
        """The Simulator"""
        if self._simulator is None:
            raise RuntimeError(
                f"Simulator access before assignment, please `set_simulator` first!"
            )
        return self._simulator

    @property
    def copy_writer(self):
        """Pg Copy Writer"""
        if self._pgsql_writer is None:
            raise RuntimeError(
                f"Copy Writer access before assignment, please `set_pgsql_writer` first!"
            )
        return self._pgsql_writer
    
    @property
    def messager(self):
        if self._messager is None:
            raise RuntimeError("Messager is not set")
        return self._messager

    async def messager_ping(self):
        if self._messager is None:
            raise RuntimeError("Messager is not set")
        return await self._messager.ping.remote()  # type:ignore

    async def generate_user_survey_response(self, survey: dict) -> str:
        """生成回答 —— 可重写
        基于智能体的记忆和当前状态，生成对问卷调查的回答。
        Args:
            survey: 需要回答的问卷 dict
        Returns:
            str: 智能体的回答
        """
        survey_prompt = process_survey_for_llm(survey)
        dialog = []

        # 添加系统提示
        system_prompt = "Please answer the survey question in first person. Follow the format requirements strictly and provide clear and specific answers."
        dialog.append({"role": "system", "content": system_prompt})

        # 添加记忆上下文
        if self._memory:
            profile_and_states = await self.status.search(survey_prompt)
            relevant_activities = await self.stream.search(survey_prompt)

            dialog.append(
                {
                    "role": "system",
                    "content": f"Answer based on following profile and states:\n{profile_and_states}\n Related activities:\n{relevant_activities}",
                }
            )

        # 添加问卷问题
        dialog.append({"role": "user", "content": survey_prompt})

        # 使用LLM生成回答
        if not self._llm_client:
            return "Sorry, I cannot answer survey questions right now."

        response = await self._llm_client.atext_request(dialog)  # type:ignore

        return response  # type:ignore

    async def _process_survey(self, survey: dict):
        survey_response = await self.generate_user_survey_response(survey)
        _date_time = datetime.now(timezone.utc)
        # Avro
        response_to_avro = [
            {
                "id": self._uuid,
                "day": await self.simulator.get_simulator_day(),
                "t": await self.simulator.get_simulator_second_from_start_of_day(),
                "survey_id": survey["id"],
                "result": survey_response,
                "created_at": int(_date_time.timestamp() * 1000),
            }
        ]
        if self._avro_file is not None:
            with open(self._avro_file["survey"], "a+b") as f:
                fastavro.writer(f, SURVEY_SCHEMA, response_to_avro, codec="snappy")
        # Pg
        if self._pgsql_writer is not None:
            if self._last_asyncio_pg_task is not None:
                await self._last_asyncio_pg_task
            _keys = [
                "id",
                "day",
                "t",
                "survey_id",
                "result",
            ]
            _data_tuples: list[tuple] = []
            # str to json
            for _dict in response_to_avro:
                res = _dict["result"]
                _dict["result"] = json.dumps(
                    {
                        "result": res,
                    }
                )
                _data_list = [_dict[k] for k in _keys]
                # created_at
                _data_list.append(_date_time)
                _data_tuples.append(tuple(_data_list))
            self._last_asyncio_pg_task = (
                self._pgsql_writer.async_write_survey.remote(  # type:ignore
                    _data_tuples
                )
            )
        await self.messager.send_message.remote(f"exps/{self._exp_id}/user_payback", {"count": 1})# type:ignore

    async def generate_user_chat_response(self, question: str) -> str:
        """生成回答 —— 可重写
        基于智能体的记忆和当前状态，生成对问题的回答。
        Args:
            question: 需要回答的问题

        Returns:
            str: 智能体的回答
        """
        dialog = []

        # 添加系统提示
        system_prompt = "Please answer the question in first person and keep the response concise and clear."
        dialog.append({"role": "system", "content": system_prompt})

        # 添加记忆上下文
        if self._memory:
            profile_and_states = await self.status.search(question, top_k=10)
            relevant_activities = await self.stream.search(question, top_k=10)

            dialog.append(
                {
                    "role": "system",
                    "content": f"Answer based on following profile and states:\n{profile_and_states}\n Related activities:\n{relevant_activities}",
                }
            )

        # 添加用户问题
        dialog.append({"role": "user", "content": question})

        # 使用LLM生成回答
        if not self._llm_client:
            return "Sorry, I cannot answer questions right now."

        response = await self._llm_client.atext_request(dialog)  # type:ignore

        return response  # type:ignore

    async def _process_interview(self, payload: dict):
        pg_list: list[tuple[dict, datetime]] = []
        auros: list[dict] = []
        _date_time = datetime.now(timezone.utc)
        _interview_dict = {
            "id": self._uuid,
            "day": await self.simulator.get_simulator_day(),
            "t": await self.simulator.get_simulator_second_from_start_of_day(),
            "type": 2,
            "speaker": "user",
            "content": payload["content"],
            "created_at": int(_date_time.timestamp() * 1000),
        }
        auros.append(_interview_dict)
        pg_list.append((_interview_dict, _date_time))
        question = payload["content"]
        response = await self.generate_user_chat_response(question)
        _date_time = datetime.now(timezone.utc)
        _interview_dict = {
            "id": self._uuid,
            "day": await self.simulator.get_simulator_day(),
            "t": await self.simulator.get_simulator_second_from_start_of_day(),
            "type": 2,
            "speaker": "",
            "content": response,
            "created_at": int(_date_time.timestamp() * 1000),
        }
        auros.append(_interview_dict)
        pg_list.append((_interview_dict, _date_time))
        # Avro
        if self._avro_file is not None:
            with open(self._avro_file["dialog"], "a+b") as f:
                fastavro.writer(f, DIALOG_SCHEMA, auros, codec="snappy")
        # Pg
        if self._pgsql_writer is not None:
            if self._last_asyncio_pg_task is not None:
                await self._last_asyncio_pg_task
            _keys = ["id", "day", "t", "type", "speaker", "content", "created_at"]
            _data = [
                tuple([_dict[k] if k != "created_at" else _date_time for k in _keys])
                for _dict, _date_time in pg_list
            ]
            self._last_asyncio_pg_task = (
                self._pgsql_writer.async_write_dialog.remote(  # type:ignore
                    _data
                )
            )
        await self.messager.send_message.remote(f"exps/{self._exp_id}/user_payback", {"count": 1})# type:ignore
        print(f"Sent payback message to {self._exp_id}")

    async def process_agent_chat_response(self, payload: dict) -> str:
        resp = f"Agent {self._uuid} received agent chat response: {payload}"
        logger.info(resp)
        return resp

    async def _process_agent_chat(self, payload: dict):
        pg_list: list[tuple[dict, datetime]] = []
        auros: list[dict] = []
        _date_time = datetime.now(timezone.utc)
        _chat_dict = {
            "id": self._uuid,
            "day": payload["day"],
            "t": payload["t"],
            "type": 1,
            "speaker": payload["from"],
            "content": payload["content"],
            "created_at": int(_date_time.timestamp() * 1000),
        }
        auros.append(_chat_dict)
        pg_list.append((_chat_dict, _date_time))
        asyncio.create_task(self.process_agent_chat_response(payload))
        # Avro
        if self._avro_file is not None:
            with open(self._avro_file["dialog"], "a+b") as f:
                fastavro.writer(f, DIALOG_SCHEMA, auros, codec="snappy")
        # Pg
        if self._pgsql_writer is not None:
            if self._last_asyncio_pg_task is not None:
                await self._last_asyncio_pg_task
            _keys = ["id", "day", "t", "type", "speaker", "content", "created_at"]
            _data = [
                tuple([_dict[k] if k != "created_at" else _date_time for k in _keys])
                for _dict, _date_time in pg_list
            ]
            self._last_asyncio_pg_task = (
                self._pgsql_writer.async_write_dialog.remote(  # type:ignore
                    _data
                )
            )

    # Callback functions for MQTT message
    async def handle_agent_chat_message(self, payload: dict):
        """处理收到的消息，识别发送者"""
        # 从消息中解析发送者 ID 和消息内容
        logger.info(f"Agent {self._uuid} received agent chat message: {payload}")
        asyncio.create_task(self._process_agent_chat(payload))

    async def handle_user_chat_message(self, payload: dict):
        """处理收到的消息，识别发送者"""
        # 从消息中解析发送者 ID 和消息内容
        logger.info(f"Agent {self._uuid} received user chat message: {payload}")
        asyncio.create_task(self._process_interview(payload))

    async def handle_user_survey_message(self, payload: dict):
        """处理收到的消息，识别发送者"""
        # 从消息中解析发送者 ID 和消息内容
        logger.info(f"Agent {self._uuid} received user survey message: {payload}")
        asyncio.create_task(self._process_survey(payload["data"]))

    async def handle_gather_message(self, payload: Any):
        raise NotImplementedError

    # MQTT send message
    async def _send_message(self, to_agent_uuid: str, payload: dict, sub_topic: str):
        """通过 Messager 发送消息"""
        if self._messager is None:
            raise RuntimeError("Messager is not set")
        topic = f"exps/{self._exp_id}/agents/{to_agent_uuid}/{sub_topic}"
        await self._messager.send_message.remote(  # type:ignore
            topic,
            payload,
            self._uuid,
            to_agent_uuid,
        )

    async def send_message_to_agent(
        self, to_agent_uuid: str, content: str, type: str = "social"
    ):
        """通过 Messager 发送消息"""
        if self._messager is None:
            raise RuntimeError("Messager is not set")
        if type not in ["social", "economy"]:
            logger.warning(f"Invalid message type: {type}, sent from {self._uuid}")
        payload = {
            "from": self._uuid,
            "content": content,
            "type": type,
            "timestamp": int(datetime.now().timestamp() * 1000),
            "day": await self.simulator.get_simulator_day(),
            "t": await self.simulator.get_simulator_second_from_start_of_day(),
        }
        await self._send_message(to_agent_uuid, payload, "agent-chat")
        pg_list: list[tuple[dict, datetime]] = []
        auros: list[dict] = []
        _date_time = datetime.now(timezone.utc)
        _message_dict = {
            "id": self._uuid,
            "day": await self.simulator.get_simulator_day(),
            "t": await self.simulator.get_simulator_second_from_start_of_day(),
            "type": 1,
            "speaker": self._uuid,
            "content": content,
            "created_at": int(datetime.now().timestamp() * 1000),
        }
        auros.append(_message_dict)
        pg_list.append((_message_dict, _date_time))
        # Avro
        if self._avro_file is not None and type == "social":
            with open(self._avro_file["dialog"], "a+b") as f:
                fastavro.writer(f, DIALOG_SCHEMA, auros, codec="snappy")
        # Pg
        if self._pgsql_writer is not None and type == "social":
            if self._last_asyncio_pg_task is not None:
                await self._last_asyncio_pg_task
            _keys = ["id", "day", "t", "type", "speaker", "content", "created_at"]
            _data = [
                tuple([_dict[k] if k != "created_at" else _date_time for k in _keys])
                for _dict, _date_time in pg_list
            ]
            self._last_asyncio_pg_task = (
                self._pgsql_writer.async_write_dialog.remote(  # type:ignore
                    _data
                )
            )

    # Agent logic
    @abstractmethod
    async def forward(self) -> None:
        """智能体行为逻辑"""
        raise NotImplementedError

    async def run(self) -> None:
        """
        统一的Agent执行入口
        当_blocked为True时，不执行forward方法
        """
        if self._messager is not None:
            await self._messager.ping.remote()  # type:ignore
        if not self._blocked:
            await self.forward()
