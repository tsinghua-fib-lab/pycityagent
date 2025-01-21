import asyncio
import json
import logging
import time
import uuid
from collections.abc import Callable
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional, Type, Union
from uuid import UUID

import fastavro
import pyproj
import ray
from langchain_core.embeddings import Embeddings

from ..agent import Agent, InstitutionAgent
from ..economy.econ_client import EconomyClient
from ..environment import Simulator
from ..llm.llm import LLM
from ..llm.llmconfig import LLMConfig
from ..memory import FaissQuery, Memory
from ..message import Messager
from ..metrics import MlflowClient
from ..utils import (DIALOG_SCHEMA, INSTITUTION_STATUS_SCHEMA, PROFILE_SCHEMA,
                     STATUS_SCHEMA, SURVEY_SCHEMA)

logger = logging.getLogger("pycityagent")


@ray.remote
class AgentGroup:
    def __init__(
        self,
        agent_class: Union[type[Agent], list[type[Agent]]],
        number_of_agents: Union[int, list[int]],
        memory_config_function_group: dict[type[Agent], Callable],
        config: dict,
        exp_name: str,
        exp_id: str | UUID,
        enable_avro: bool,
        avro_path: Path,
        enable_pgsql: bool,
        pgsql_writer: ray.ObjectRef,
        message_interceptor: ray.ObjectRef,
        mlflow_run_id: str,
        embedding_model: Embeddings,
        logging_level: int,
        agent_config_file: Optional[dict[type[Agent], str]] = None,
        environment: Optional[dict[str, str]] = None,
    ):
        logger.setLevel(logging_level)
        self._uuid = str(uuid.uuid4())
        if not isinstance(agent_class, list):
            agent_class = [agent_class]
        if not isinstance(number_of_agents, list):
            number_of_agents = [number_of_agents]
        self.agent_class = agent_class
        self.number_of_agents = number_of_agents
        self.memory_config_function_group = memory_config_function_group
        self.agents: list[Agent] = []
        self.id2agent: dict[str, Agent] = {}
        self.config = config
        self.exp_id = exp_id
        self.enable_avro = enable_avro
        self.enable_pgsql = enable_pgsql
        self.embedding_model = embedding_model
        self.agent_config_file = agent_config_file
        if enable_avro:
            self.avro_path = avro_path / f"{self._uuid}"
            self.avro_path.mkdir(parents=True, exist_ok=True)
            self.avro_file = {
                "profile": self.avro_path / f"profile.avro",
                "dialog": self.avro_path / f"dialog.avro",
                "status": self.avro_path / f"status.avro",
                "survey": self.avro_path / f"survey.avro",
            }
        if self.enable_pgsql:
            pass
        # Mlflow
        _mlflow_config = config.get("metric_request", {}).get("mlflow")
        if _mlflow_config:
            logger.info(f"-----Creating Mlflow client in AgentGroup {self._uuid} ...")
            self.mlflow_client = MlflowClient(
                config=_mlflow_config,
                experiment_uuid=self.exp_id,  # type:ignore
                mlflow_run_name=f"{exp_name}_{1000*int(time.time())}",
                experiment_name=exp_name,
                run_id=mlflow_run_id,
            )
        else:
            self.mlflow_client = None

        # prepare Messager
        if "mqtt" in config["simulator_request"]:
            self.messager = Messager.remote(
                hostname=config["simulator_request"]["mqtt"]["server"],  # type:ignore
                port=config["simulator_request"]["mqtt"]["port"],
                username=config["simulator_request"]["mqtt"].get("username", None),
                password=config["simulator_request"]["mqtt"].get("password", None),
            )
        else:
            self.messager = None

        self.message_dispatch_task = None
        self._pgsql_writer = pgsql_writer
        self._message_interceptor = message_interceptor
        self._last_asyncio_pg_task = None  # 将SQL写入的IO隐藏到计算任务后
        self.initialized = False
        self.id2agent = {}
        # prepare LLM client
        llmConfig = LLMConfig(config["llm_request"])
        logger.info(f"-----Creating LLM client in AgentGroup {self._uuid} ...")
        self.llm = LLM(llmConfig)

        # prepare Simulator
        logger.info(f"-----Creating Simulator in AgentGroup {self._uuid} ...")
        self.simulator = Simulator(config["simulator_request"])
        self.projector = pyproj.Proj(self.simulator.map.header["projection"])
        self.simulator.set_environment(environment)
        # prepare Economy client
        logger.info(f"-----Creating Economy client in AgentGroup {self._uuid} ...")
        self.economy_client = EconomyClient(
            config["simulator_request"]["simulator"]["server"]
        )

        # set FaissQuery
        if self.embedding_model is not None:
            self.faiss_query = FaissQuery(
                embeddings=self.embedding_model,
            )
        else:
            self.faiss_query = None
        for i in range(len(number_of_agents)):
            agent_class_i = agent_class[i]
            number_of_agents_i = number_of_agents[i]
            for j in range(number_of_agents_i):
                memory_config_function_group_i = memory_config_function_group[agent_class_i]
                extra_attributes, profile, base = memory_config_function_group_i()
                memory = Memory(config=extra_attributes, profile=profile, base=base)
                agent = agent_class_i(
                    name=f"{agent_class_i.__name__}_{i}",  # type: ignore
                    memory=memory,
                    llm_client=self.llm,
                    economy_client=self.economy_client,
                    simulator=self.simulator,
                )
                agent.set_exp_id(self.exp_id)  # type: ignore
                if self.messager is not None:
                    agent.set_messager(self.messager)
                if self.mlflow_client is not None:
                    agent.set_mlflow_client(self.mlflow_client)  # type: ignore
                if self.enable_avro:
                    agent.set_avro_file(self.avro_file)  # type: ignore
                if self.enable_pgsql:
                    agent.set_pgsql_writer(self._pgsql_writer)
                if self.agent_config_file is not None and self.agent_config_file[agent_class_i]:
                    agent.load_from_file(self.agent_config_file[agent_class_i])
                if self._message_interceptor is not None:
                    agent.set_message_interceptor(self._message_interceptor)
                self.agents.append(agent)
                self.id2agent[agent._uuid] = agent

    @property
    def agent_count(self):
        return self.number_of_agents

    @property
    def agent_uuids(self):
        return list(self.id2agent.keys())

    @property
    def agent_type(self):
        return self.agent_class

    def get_agent_count(self):
        return self.agent_count

    def get_agent_uuids(self):
        return self.agent_uuids

    def get_agent_type(self):
        return self.agent_type

    async def __aexit__(self, exc_type, exc_value, traceback):
        self.message_dispatch_task.cancel()  # type: ignore
        await asyncio.gather(self.message_dispatch_task, return_exceptions=True)  # type: ignore

    async def insert_agent(self):
        bind_tasks = []
        for agent in self.agents:
            bind_tasks.append(agent.bind_to_simulator())  # type: ignore
        await asyncio.gather(*bind_tasks)

    async def init_agents(self):
        logger.debug(f"-----Initializing Agents in AgentGroup {self._uuid} ...")
        logger.debug(f"-----Binding Agents to Simulator in AgentGroup {self._uuid} ...")
        while True:
            day = await self.simulator.get_simulator_day()
            if day == 0:
                break
            await asyncio.sleep(1)
        await self.insert_agent()
        self.id2agent = {agent._uuid: agent for agent in self.agents}
        logger.debug(f"-----Binding Agents to Messager in AgentGroup {self._uuid} ...")
        assert self.messager is not None
        await self.messager.connect.remote()
        if await self.messager.is_connected.remote():
            await self.messager.start_listening.remote()
            topics = []
            agents = []
            for agent in self.agents:
                agent.set_messager(self.messager)
                topic = (f"exps/{self.exp_id}/agents/{agent._uuid}/#", 1)
                topics.append(topic)
                agents.append(agent.uuid)
            await self.messager.subscribe.remote(topics, agents)
        self.message_dispatch_task = asyncio.create_task(self.message_dispatch())
        if self.enable_avro:
            logger.debug(f"-----Creating Avro files in AgentGroup {self._uuid} ...")
            # profile
            if not issubclass(type(self.agents[0]), InstitutionAgent):
                filename = self.avro_file["profile"]
                with open(filename, "wb") as f:
                    profiles = []
                    for agent in self.agents:
                        profile = await agent.status.profile.export()
                        profile = profile[0]
                        profile["id"] = agent._uuid
                        profiles.append(profile)
                    fastavro.writer(f, PROFILE_SCHEMA, profiles)

            # dialog
            filename = self.avro_file["dialog"]
            with open(filename, "wb") as f:
                dialogs = []
                fastavro.writer(f, DIALOG_SCHEMA, dialogs)

            # status
            filename = self.avro_file["status"]
            with open(filename, "wb") as f:
                statuses = []
                if not issubclass(type(self.agents[0]), InstitutionAgent):
                    fastavro.writer(f, STATUS_SCHEMA, statuses)
                else:
                    fastavro.writer(f, INSTITUTION_STATUS_SCHEMA, statuses)

            # survey
            filename = self.avro_file["survey"]
            with open(filename, "wb") as f:
                surveys = []
                fastavro.writer(f, SURVEY_SCHEMA, surveys)

        if self.enable_pgsql:
            if not issubclass(type(self.agents[0]), InstitutionAgent):
                profiles: list[Any] = []
                for agent in self.agents:
                    profile = await agent.status.profile.export()
                    profile = profile[0]
                    profile["id"] = agent._uuid
                    profiles.append(
                        (
                            agent._uuid,
                            profile.get("name", ""),
                            json.dumps(
                                {
                                    k: v
                                    for k, v in profile.items()
                                    if k not in {"id", "name"}
                                }
                            ),
                        )
                    )
            else:
                profiles: list[Any] = []
                for agent in self.agents:
                    profile = await agent.status.profile.export()
                    profile = profile[0]
                    profile["id"] = agent._uuid
                    profiles.append(
                        (
                            agent._uuid,
                            profile.get("name", ""),
                            json.dumps(
                                {
                                    k: v
                                    for k, v in profile.items()
                                    if k not in {"id", "name"}
                                }
                            ),
                        )
                    )
            await self._pgsql_writer.async_write_profile.remote(  # type:ignore
                profiles
            )
        if self.faiss_query is not None:
            logger.debug(f"-----Initializing embeddings in AgentGroup {self._uuid} ...")
            embedding_tasks = []
            for agent in self.agents:
                embedding_tasks.append(agent.memory.initialize_embeddings())
                agent.memory.set_search_components(
                    self.faiss_query, self.embedding_model
                )
                agent.memory.set_simulator(self.simulator)
            await asyncio.gather(*embedding_tasks)
            logger.debug(f"-----Embedding initialized in AgentGroup {self._uuid} ...")

        self.initialized = True
        logger.debug(f"-----AgentGroup {self._uuid} initialized")

    async def filter(
        self,
        types: Optional[list[Type[Agent]]] = None,
        keys: Optional[list[str]] = None,
        values: Optional[list[Any]] = None,
    ) -> list[str]:
        filtered_uuids = []
        for agent in self.agents:
            add = True
            if types:
                if agent.__class__ in types:
                    if keys:
                        for key in keys:
                            assert values is not None
                            if not agent.status.get(key) == values[keys.index(key)]:
                                add = False
                                break
                    if add:
                        filtered_uuids.append(agent._uuid)
            elif keys:
                for key in keys:
                    assert values is not None
                    if not agent.status.get(key) == values[keys.index(key)]:
                        add = False
                        break
                if add:
                    filtered_uuids.append(agent._uuid)
        return filtered_uuids

    async def gather(
        self, content: str, target_agent_uuids: Optional[list[str]] = None
    ):
        logger.debug(f"-----Gathering {content} from all agents in group {self._uuid}")
        results = {}
        if target_agent_uuids is None:
            target_agent_uuids = self.agent_uuids
        for agent in self.agents:
            if agent._uuid in target_agent_uuids:
                results[agent._uuid] = await agent.status.get(content)
        return results

    async def update(self, target_agent_uuid: str, target_key: str, content: Any):
        logger.debug(
            f"-----Updating {target_key} for agent {target_agent_uuid} in group {self._uuid}"
        )
        agent = self.id2agent[target_agent_uuid]
        await agent.status.update(target_key, content)

    async def update_environment(self, key: str, value: str):
        self.simulator.update_environment(key, value)

    async def message_dispatch(self):
        logger.debug(f"-----Starting message dispatch for group {self._uuid}")
        while True:
            assert self.messager is not None
            if not await self.messager.is_connected.remote():
                logger.warning(
                    "Messager is not connected. Skipping message processing."
                )
                break

            # Step 1: 获取消息
            messages = await self.messager.fetch_messages.remote()
            logger.info(f"Group {self._uuid} received {len(messages)} messages")

            # Step 2: 分发消息到对应的 Agent
            for message in messages:
                topic = message.topic.value
                payload = message.payload

                # 添加解码步骤，将bytes转换为str
                if isinstance(payload, bytes):
                    payload = payload.decode("utf-8")
                    payload = json.loads(payload)

                # 提取 agent_id（主题格式为 "exps/{exp_id}/agents/{agent_uuid}/{topic_type}"）
                _, _, _, agent_uuid, topic_type = topic.strip("/").split("/")

                if agent_uuid in self.id2agent:
                    agent = self.id2agent[agent_uuid]
                    # topic_type: agent-chat, user-chat, user-survey, gather
                    if topic_type == "agent-chat":
                        await agent.handle_agent_chat_message(payload)
                    elif topic_type == "user-chat":
                        await agent.handle_user_chat_message(payload)
                    elif topic_type == "user-survey":
                        await agent.handle_user_survey_message(payload)
                    elif topic_type == "gather":
                        await agent.handle_gather_message(payload)
            await asyncio.sleep(3)

    async def save_status(
        self, simulator_day: Optional[int] = None, simulator_t: Optional[int] = None
    ):
        _statuses_time_list: list[tuple[dict, datetime]] = []
        if self.enable_avro:
            logger.debug(f"-----Saving status for group {self._uuid} with Avro")
            avros = []
            if simulator_day is not None:
                _day = simulator_day
            else:
                _day = await self.simulator.get_simulator_day()
            if simulator_t is not None:
                _t = simulator_t
            else:
                _t = await self.simulator.get_simulator_second_from_start_of_day()
            if not issubclass(type(self.agents[0]), InstitutionAgent):
                for agent in self.agents:
                    _date_time = datetime.now(timezone.utc)
                    position = await agent.status.get("position")
                    x = position["xy_position"]["x"]
                    y = position["xy_position"]["y"]
                    lng, lat = self.projector(x, y, inverse=True)
                    if "aoi_position" in position:
                        parent_id = position["aoi_position"]["aoi_id"]
                    elif "lane_position" in position:
                        parent_id = position["lane_position"]["lane_id"]
                    else:
                        parent_id = -1
                    hunger_satisfaction = await agent.status.get("hunger_satisfaction")
                    energy_satisfaction = await agent.status.get("energy_satisfaction")
                    safety_satisfaction = await agent.status.get("safety_satisfaction")
                    social_satisfaction = await agent.status.get("social_satisfaction")
                    action = await agent.status.get("current_step")
                    action = action["intention"]
                    avro = {
                        "id": agent._uuid,
                        "day": _day,
                        "t": _t,
                        "lng": lng,
                        "lat": lat,
                        "parent_id": parent_id,
                        "action": action,
                        "hungry": hunger_satisfaction,
                        "tired": energy_satisfaction,
                        "safe": safety_satisfaction,
                        "social": social_satisfaction,
                        "created_at": int(_date_time.timestamp() * 1000),
                    }
                    avros.append(avro)
                    _statuses_time_list.append((avro, _date_time))
                with open(self.avro_file["status"], "a+b") as f:
                    fastavro.writer(f, STATUS_SCHEMA, avros, codec="snappy")
            else:
                for agent in self.agents:
                    _date_time = datetime.now(timezone.utc)
                    try:
                        nominal_gdp = await agent.status.get("nominal_gdp")
                    except:
                        nominal_gdp = []
                    try:
                        real_gdp = await agent.status.get("real_gdp")
                    except:
                        real_gdp = []
                    try:
                        unemployment = await agent.status.get("unemployment")
                    except:
                        unemployment = []
                    try:
                        wages = await agent.status.get("wages")
                    except:
                        wages = []
                    try:
                        prices = await agent.status.get("prices")
                    except:
                        prices = []
                    try:
                        inventory = await agent.status.get("inventory")
                    except:
                        inventory = 0
                    try:
                        price = await agent.status.get("price")
                    except:
                        price = 0.0
                    try:
                        interest_rate = await agent.status.get("interest_rate")
                    except:
                        interest_rate = 0.0
                    try:
                        bracket_cutoffs = await agent.status.get("bracket_cutoffs")
                    except:
                        bracket_cutoffs = []
                    try:
                        bracket_rates = await agent.status.get("bracket_rates")
                    except:
                        bracket_rates = []
                    try:
                        employees = await agent.status.get("employees")
                    except:
                        employees = []
                    avro = {
                        "id": agent._uuid,
                        "day": _day,
                        "t": _t,
                        "type": await agent.status.get("type"),
                        "nominal_gdp": nominal_gdp,
                        "real_gdp": real_gdp,
                        "unemployment": unemployment,
                        "wages": wages,
                        "prices": prices,
                        "inventory": inventory,
                        "price": price,
                        "interest_rate": interest_rate,
                        "bracket_cutoffs": bracket_cutoffs,
                        "bracket_rates": bracket_rates,
                        "employees": employees,
                    }
                    avros.append(avro)
                    _statuses_time_list.append((avro, _date_time))
                with open(self.avro_file["status"], "a+b") as f:
                    fastavro.writer(f, INSTITUTION_STATUS_SCHEMA, avros, codec="snappy")
        if self.enable_pgsql:
            logger.debug(f"-----Saving status for group {self._uuid} with PgSQL")
            if simulator_day is not None:
                _day = simulator_day
            else:
                _day = await self.simulator.get_simulator_day()
            if simulator_t is not None:
                _t = simulator_t
            else:
                _t = await self.simulator.get_simulator_second_from_start_of_day()
            # data already acquired from Avro part
            if len(_statuses_time_list) > 0:
                for _status_dict, _date_time in _statuses_time_list:
                    for key in ["lng", "lat", "parent_id"]:
                        if key not in _status_dict:
                            _status_dict[key] = -1
                    for key in [
                        "action",
                    ]:
                        if key not in _status_dict:
                            _status_dict[key] = ""
                    for key in [
                        "friend_ids",
                    ]:
                        if key not in _status_dict:
                            _status_dict[key] = []
                    _status_dict["created_at"] = _date_time
            else:
                if not issubclass(type(self.agents[0]), InstitutionAgent):
                    for agent in self.agents:
                        _date_time = datetime.now(timezone.utc)
                        position = await agent.status.get("position")
                        x = position["xy_position"]["x"]
                        y = position["xy_position"]["y"]
                        lng, lat = self.projector(x, y, inverse=True)
                        if "aoi_position" in position:
                            parent_id = position["aoi_position"]["aoi_id"]
                        elif "lane_position" in position:
                            parent_id = position["lane_position"]["lane_id"]
                        else:
                            parent_id = -1
                        hunger_satisfaction = await agent.status.get(
                            "hunger_satisfaction"
                        )
                        energy_satisfaction = await agent.status.get(
                            "energy_satisfaction"
                        )
                        safety_satisfaction = await agent.status.get(
                            "safety_satisfaction"
                        )
                        social_satisfaction = await agent.status.get(
                            "social_satisfaction"
                        )
                        friend_ids = await agent.status.get("friends")
                        action = await agent.status.get("current_step")
                        action = action["intention"]
                        _status_dict = {
                            "id": agent._uuid,
                            "day": _day,
                            "t": _t,
                            "lng": lng,
                            "lat": lat,
                            "parent_id": parent_id,
                            "friend_ids": [
                                str(_friend_id) for _friend_id in friend_ids
                            ],
                            "action": action,
                            "hungry": hunger_satisfaction,
                            "tired": energy_satisfaction,
                            "safe": safety_satisfaction,
                            "social": social_satisfaction,
                            "created_at": _date_time,
                        }
                        _statuses_time_list.append((_status_dict, _date_time))
                else:
                    # institution
                    for agent in self.agents:
                        _date_time = datetime.now(timezone.utc)
                        position = await agent.status.get("position")
                        x = position["xy_position"]["x"]
                        y = position["xy_position"]["y"]
                        lng, lat = self.projector(x, y, inverse=True)
                        # ATTENTION: no valid position for an institution
                        parent_id = -1
                        try:
                            nominal_gdp = await agent.status.get("nominal_gdp")
                        except:
                            nominal_gdp = []
                        try:
                            real_gdp = await agent.status.get("real_gdp")
                        except:
                            real_gdp = []
                        try:
                            unemployment = await agent.status.get("unemployment")
                        except:
                            unemployment = []
                        try:
                            wages = await agent.status.get("wages")
                        except:
                            wages = []
                        try:
                            prices = await agent.status.get("prices")
                        except:
                            prices = []
                        try:
                            inventory = await agent.status.get("inventory")
                        except:
                            inventory = 0
                        try:
                            price = await agent.status.get("price")
                        except:
                            price = 0.0
                        try:
                            interest_rate = await agent.status.get("interest_rate")
                        except:
                            interest_rate = 0.0
                        try:
                            bracket_cutoffs = await agent.status.get("bracket_cutoffs")
                        except:
                            bracket_cutoffs = []
                        try:
                            bracket_rates = await agent.status.get("bracket_rates")
                        except:
                            bracket_rates = []
                        try:
                            employees = await agent.status.get("employees")
                        except:
                            employees = []
                        try:
                            friend_ids = await agent.status.get("friends")
                        except:
                            friend_ids = []
                        _status_dict = {
                            "id": agent._uuid,
                            "day": _day,
                            "t": _t,
                            "lng": lng,
                            "lat": lat,
                            "parent_id": parent_id,
                            "friend_ids": [
                                str(_friend_id) for _friend_id in friend_ids
                            ],
                            "action": "",
                            "type": await agent.status.get("type"),
                            "nominal_gdp": nominal_gdp,
                            "real_gdp": real_gdp,
                            "unemployment": unemployment,
                            "wages": wages,
                            "prices": prices,
                            "inventory": inventory,
                            "price": price,
                            "interest_rate": interest_rate,
                            "bracket_cutoffs": bracket_cutoffs,
                            "bracket_rates": bracket_rates,
                            "employees": employees,
                            "created_at": _date_time,
                        }
                        _statuses_time_list.append((_status_dict, _date_time))
            to_update_statues: list[tuple] = []
            for _status_dict, _ in _statuses_time_list:
                BASIC_KEYS = [
                    "id",
                    "day",
                    "t",
                    "lng",
                    "lat",
                    "parent_id",
                    "friend_ids",
                    "action",
                    "created_at",
                ]
                _data = [_status_dict[k] for k in BASIC_KEYS if k != "created_at"]
                _other_dict = json.dumps(
                    {k: v for k, v in _status_dict.items() if k not in BASIC_KEYS}
                )
                _data.append(_other_dict)
                _data.append(_status_dict["created_at"])
                to_update_statues.append(tuple(_data))
            if self._last_asyncio_pg_task is not None:
                await self._last_asyncio_pg_task
            self._last_asyncio_pg_task = (
                self._pgsql_writer.async_write_status.remote(  # type:ignore
                    to_update_statues
                )
            )

    def get_llm_consumption(self):
        return self.llm.get_consumption()

    async def step(self):
        try:
            tasks = [agent.run() for agent in self.agents]
            await asyncio.gather(*tasks)
        except Exception as e:
            import traceback

            logger.error(f"模拟器运行错误: {str(e)}\n{traceback.format_exc()}")
            raise RuntimeError(str(e)) from e

    async def save(self, day: int, t: int):
        try:
            await self.save_status(day, t)
        except Exception as e:
            import traceback

            logger.error(f"模拟器运行错误: {str(e)}\n{traceback.format_exc()}")
            raise RuntimeError(str(e)) from e
