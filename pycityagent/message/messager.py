import asyncio
from collections import defaultdict
import json
import logging
import math
from aiomqtt import Client

logger = logging.getLogger("pycityagent")

class Messager:
    def __init__(
        self, hostname:str, port:int=1883, username=None, password=None, timeout=math.inf
    ):
        self.client = Client(
            hostname, port=port, username=username, password=password, timeout=timeout
        )
        self.connected = False  # 是否已连接标志
        self.message_queue = asyncio.Queue()  # 用于存储接收到的消息
        self.subscribers = {}  # 订阅者信息，topic -> Agent 映射

    async def connect(self):
        try:
            await self.client.__aenter__()
            self.connected = True
            logger.info("Connected to MQTT Broker")
        except Exception as e:
            self.connected = False
            logger.error(f"Failed to connect to MQTT Broker: {e}")

    async def disconnect(self):
        await self.client.__aexit__(None, None, None)
        self.connected = False
        logger.info("Disconnected from MQTT Broker")

    def is_connected(self):
        """检查是否成功连接到 Broker"""
        return self.connected

    async def subscribe(self, topic, agent):
        if not self.is_connected():
            logger.error(
                f"Cannot subscribe to {topic} because not connected to the Broker."
            )
            return
        await self.client.subscribe(topic)
        self.subscribers[topic] = agent
        logger.info(f"Subscribed to {topic} for Agent {agent._uuid}")

    async def receive_messages(self):
        """监听并将消息存入队列"""
        async for message in self.client.messages:
            await self.message_queue.put(message)

    async def fetch_messages(self):
        """从队列中批量获取消息"""
        messages = []
        while not self.message_queue.empty():
            messages.append(await self.message_queue.get())
        return messages

    async def send_message(self, topic: str, payload: dict):
        """通过 Messager 发送消息"""
        message = json.dumps(payload, default=str)
        await self.client.publish(topic, message)
        logger.info(f"Message sent to {topic}: {message}")

    async def start_listening(self):
        """启动消息监听任务"""
        if self.is_connected():
            asyncio.create_task(self.receive_messages())
        else:
            logger.error("Cannot start listening because not connected to the Broker.")
