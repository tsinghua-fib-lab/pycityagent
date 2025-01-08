import asyncio
import json
import logging
import math
from typing import Any, List, Union

import ray
from aiomqtt import Client

logger = logging.getLogger("pycityagent")


@ray.remote
class Messager:
    def __init__(
        self, hostname: str, port: int = 1883, username=None, password=None, timeout=60
    ):
        self.client = Client(
            hostname, port=port, username=username, password=password, timeout=timeout
        )
        self.connected = False  # 是否已连接标志
        self.message_queue = asyncio.Queue()  # 用于存储接收到的消息
        self.receive_messages_task = None

    async def __aexit__(self, exc_type, exc_value, traceback):
        await self.stop()

    async def ping(self):
        await self.client.publish(topic="ping", payload="ping", qos=1)

    async def connect(self):
        for i in range(3):
            try:
                await self.client.__aenter__()
                self.connected = True
                logger.info("Connected to MQTT Broker")
                return
            except Exception as e:
                logger.error(f"Attempt {i+1}: Failed to connect to MQTT Broker: {e}")
                await asyncio.sleep(10)
        self.connected = False
        logger.error("All connection attempts failed.")

    async def disconnect(self):
        await self.client.__aexit__(None, None, None)
        self.connected = False
        logger.info("Disconnected from MQTT Broker")

    async def is_connected(self):
        """检查是否成功连接到 Broker"""
        return self.connected

    async def subscribe(
        self, topics: Union[str, List[str]], agents: Union[Any, List[Any]]
    ):
        if not await self.is_connected():
            logger.error(
                f"Cannot subscribe to {topics} because not connected to the Broker."
            )
            return
        if not isinstance(topics, list):
            topics = [topics]
        if not isinstance(agents, list):
            agents = [agents]
        await self.client.subscribe(topics, qos=1)

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
        await self.client.publish(topic=topic, payload=message, qos=1)
        logger.info(f"Message sent to {topic}: {message}")

    async def start_listening(self):
        """启动消息监听任务"""
        if await self.is_connected():
            self.receive_messages_task = asyncio.create_task(self.receive_messages())
        else:
            logger.error("Cannot start listening because not connected to the Broker.")

    async def stop(self):
        assert self.receive_messages_task is not None
        self.receive_messages_task.cancel()
        await asyncio.gather(
            self.receive_messages_task, return_exceptions=True
        )
        await self.disconnect()
