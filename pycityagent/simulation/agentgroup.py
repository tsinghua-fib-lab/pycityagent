import asyncio
from datetime import datetime
import json
import logging
import uuid
import fastavro
import ray
from uuid import UUID
from pycityagent.agent import Agent, CitizenAgent
from pycityagent.economy.econ_client import EconomyClient
from pycityagent.environment.simulator import Simulator
from pycityagent.llm.llm import LLM
from pycityagent.llm.llmconfig import LLMConfig
from pycityagent.message import Messager
from pycityagent.utils import STATUS_SCHEMA
from typing import Any

@ray.remote
class AgentGroup:
    def __init__(self, agents: list[Agent], config: dict, exp_id: str|UUID, avro_file: dict):
        self.agents = agents
        self.config = config
        self.exp_id = exp_id
        self.avro_file = avro_file
        self._uuid = uuid.uuid4()
        self.messager = Messager(
            hostname=config["simulator_request"]["mqtt"]["server"],
            port=config["simulator_request"]["mqtt"]["port"],
            username=config["simulator_request"]["mqtt"].get("username", None),
            password=config["simulator_request"]["mqtt"].get("password", None),
        )
        self.initialized = False
        self.id2agent = {}
        # Step:1 prepare LLM client
        llmConfig = LLMConfig(config["llm_request"])
        logging.info("-----Creating LLM client in remote...")
        self.llm = LLM(llmConfig)

        # Step:2 prepare Simulator
        logging.info("-----Creating Simulator in remote...")
        self.simulator = Simulator(config["simulator_request"])

        # Step:3 prepare Economy client
        if "economy" in config["simulator_request"]:
            logging.info("-----Creating Economy client in remote...")
            self.economy_client = EconomyClient(
                config["simulator_request"]["economy"]["server"]
            )
        else:
            self.economy_client = None

        for agent in self.agents:
            agent.set_exp_id(self.exp_id)
            agent.set_llm_client(self.llm)
            agent.set_simulator(self.simulator)
            if self.economy_client is not None:
                agent.set_economy_client(self.economy_client)
            agent.set_messager(self.messager)

    async def init_agents(self):
        for agent in self.agents:
            await agent.bind_to_simulator()
        self.id2agent = {agent._uuid: agent for agent in self.agents}
        await self.messager.connect()
        if self.messager.is_connected():
            await self.messager.start_listening()
            for agent in self.agents:
                agent.set_messager(self.messager)
                topic = f"exps/{self.exp_id}/agents/{agent._uuid}/agent-chat"
                await self.messager.subscribe(topic, agent)
                topic = f"exps/{self.exp_id}/agents/{agent._uuid}/user-chat"
                await self.messager.subscribe(topic, agent)
                topic = f"exps/{self.exp_id}/agents/{agent._uuid}/user-survey"
                await self.messager.subscribe(topic, agent)
                topic = f"exps/{self.exp_id}/agents/{agent._uuid}/gather"
                await self.messager.subscribe(topic, agent)
        self.initialized = True
        self.message_dispatch_task = asyncio.create_task(self.message_dispatch())
        
    async def gather(self, content: str):
        results = {}
        for agent in self.agents:
            results[agent._uuid] = await agent.memory.get(content)
        return results

    async def update(self, target_agent_uuid: str, target_key: str, content: Any):
        agent = self.id2agent[target_agent_uuid]
        await agent.memory.update(target_key, content)

    async def message_dispatch(self):
        while True:
            if not self.messager.is_connected():
                logging.warning("Messager is not connected. Skipping message processing.")

            # Step 1: 获取消息
            messages = await self.messager.fetch_messages()
            logging.info(f"Group {self._uuid} received {len(messages)} messages")

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
                    
                if uuid.UUID(agent_uuid) in self.id2agent:
                    agent = self.id2agent[uuid.UUID(agent_uuid)]
                    # topic_type: agent-chat, user-chat, user-survey, gather
                    if topic_type == "agent-chat":
                        await agent.handle_agent_chat_message(payload)
                    elif topic_type == "user-chat":
                        await agent.handle_user_chat_message(payload)
                    elif topic_type == "user-survey":
                        await agent.handle_user_survey_message(payload)
                    elif topic_type == "gather":
                        await agent.handle_gather_message(payload)

            await asyncio.sleep(0.5)

    async def step(self):
        if not self.initialized:
            await self.init_agents()

        tasks = [agent.run() for agent in self.agents]
        await asyncio.gather(*tasks)
        avros = []
        for agent in self.agents:
            if not issubclass(type(agent), CitizenAgent):
                continue
            position = await agent.memory.get("position")
            lng = position["longlat_position"]["longitude"]
            lat = position["longlat_position"]["latitude"]
            if "aoi_position" in position:
                parent_id = position["aoi_position"]["aoi_id"]
            elif "lane_position" in position:
                parent_id = position["lane_position"]["lane_id"]
            else:
                # BUG: 需要处理
                parent_id = -1
            needs = await agent.memory.get("needs")
            action = await agent.memory.get("current_step")
            action = action["intention"]
            avro = {
                "id": str(agent._uuid),  # uuid as string
                "day": await self.simulator.get_simulator_day(),
                "t": await self.simulator.get_simulator_second_from_start_of_day(),
                "lng": lng,
                "lat": lat,
                "parent_id": parent_id,
                "action": action,
                "hungry": needs["hungry"],
                "tired": needs["tired"],
                "safe": needs["safe"],
                "social": needs["social"],
                "created_at": int(datetime.now().timestamp() * 1000),
            }
            avros.append(avro)
        with open(self.avro_file["status"], "a+b") as f:
            fastavro.writer(f, STATUS_SCHEMA, avros, codec="snappy")

    async def run(self, day: int = 1):
        """运行模拟器

        Args:
            day: 运行天数,默认为1天
        """
        try:
            # 获取开始时间
            start_time = await self.simulator.get_time()
            start_time = int(start_time)
            # 计算结束时间（秒）
            end_time = start_time + day * 24 * 3600  # 将天数转换为秒

            while True:
                current_time = await self.simulator.get_time()
                current_time = int(current_time)
                if current_time >= end_time:
                    break
                await self.step()

        except Exception as e:
            logging.error(f"模拟器运行错误: {str(e)}")
            raise
