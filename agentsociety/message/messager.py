import asyncio
import json
import logging
import time
from typing import Any, Optional, Union

import ray
from aiomqtt import Client

__all__ = [
    "Messager",
]

logger = logging.getLogger("agentsociety")


@ray.remote
class Messager:
    """
    A class to manage message sending and receiving using an MQTT protocol.

    - **Attributes**:
        - `client` (Client): An instance of the MQTT client.
        - `connected` (bool): Indicates whether the connection to the broker is established.
        - `message_queue` (asyncio.Queue): Queue for storing received messages.
        - `receive_messages_task` (Optional[Task]): Task for listening to incoming messages.
        - `_message_interceptor` (Optional[ray.ObjectRef]): Reference to a remote message interceptor object.
    """

    def __init__(
        self,
        hostname: str,
        port: int = 1883,
        username=None,
        password=None,
        timeout=60,
        message_interceptor: Optional[ray.ObjectRef] = None,
    ):
        """
        Initialize the Messager with connection parameters.

        - **Args**:
            - `hostname` (str): The hostname or IP address of the MQTT broker.
            - `port` (int, optional): Port number of the MQTT broker. Defaults to 1883.
            - `username` (str, optional): Username for broker authentication.
            - `password` (str, optional): Password for broker authentication.
            - `timeout` (int, optional): Connection timeout in seconds. Defaults to 60.
            - `message_interceptor` (Optional[ray.ObjectRef], optional): Reference to a message interceptor object.
        """
        self.client = Client(
            hostname, port=port, username=username, password=password, timeout=timeout
        )
        self.connected = False  # 是否已连接标志
        self.message_queue = asyncio.Queue()  # 用于存储接收到的消息
        self.receive_messages_task = None
        self._message_interceptor = message_interceptor
        self._log_list = []

    @property
    def message_interceptor(
        self,
    ) -> Union[None, ray.ObjectRef]:
        """
        Access the message interceptor reference.

        - **Returns**:
            - `Union[None, ray.ObjectRef]`: The message interceptor reference.
        """
        return self._message_interceptor

    def get_log_list(self):
        return self._log_list

    def clear_log_list(self):
        self._log_list = []

    def set_message_interceptor(self, message_interceptor: ray.ObjectRef):
        """
        Set the message interceptor reference.

        - **Args**:
            - `message_interceptor` (ray.ObjectRef): The message interceptor reference to be set.
        """
        self._message_interceptor = message_interceptor

    async def __aexit__(self, exc_type, exc_value, traceback):
        """
        Asynchronous exit method to ensure proper cleanup when used in an async context manager.

        - **Args**:
            - `exc_type`, `exc_value`, `traceback`: Exception information if an exception occurred.
        """
        await self.stop()

    async def ping(self):
        """
        Send a ping message to the MQTT broker.

        - **Description**:
            - Publishes a 'ping' message on the 'ping' topic with QoS level 1.
        """
        await self.client.publish(topic="ping", payload="ping", qos=1)

    async def connect(self):
        """
        Attempt to connect to the MQTT broker up to three times.

        - **Description**:
            - Tries to establish a connection to the MQTT broker. Retries up to three times with delays between attempts.
            - Logs success or failure accordingly.
        """
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
        """
        Disconnect from the MQTT broker.

        - **Description**:
            - Closes the connection to the MQTT broker and logs the disconnection.
        """
        await self.client.__aexit__(None, None, None)
        self.connected = False
        logger.info("Disconnected from MQTT Broker")

    async def is_connected(self):
        """
        Check if the connection to the broker is established.

        - **Returns**:
            - `bool`: True if connected, otherwise False.
        """
        return self.connected

    async def subscribe(
        self, topics: Union[str, list[str]], agents: Union[Any, list[Any]]
    ):
        """
        Subscribe to one or more MQTT topics.

        - **Args**:
            - `topics` (Union[str, list[str]]): Topic or list of topics to subscribe to.
            - `agents` (Union[Any, list[Any]]): Agents or list of agents associated with the subscription.
        """
        if not await self.is_connected():
            logger.error(
                f"Cannot subscribe to {topics} because not connected to the Broker."
            )
            return
        if not isinstance(topics, list):
            topics = [topics]
        if not isinstance(agents, list):
            agents = [agents]
        await self.client.subscribe(topics, qos=1)  # type: ignore

    async def receive_messages(self):
        """
        Listen for incoming messages and store them in the queue.

        - **Description**:
            - Continuously listens for incoming messages and puts them into the message queue.
        """
        async for message in self.client.messages:
            await self.message_queue.put(message)

    async def fetch_messages(self):
        """
        Retrieve all messages currently in the queue.

        - **Returns**:
            - `list[Any]`: List of messages retrieved from the queue.
        """
        messages = []
        while not self.message_queue.empty():
            messages.append(await self.message_queue.get())
        return messages

    async def send_message(
        self,
        topic: str,
        payload: dict,
        from_uuid: Optional[str] = None,
        to_uuid: Optional[str] = None,
    ):
        """
        Send a message through the MQTT broker.

        - **Args**:
            - `topic` (str): Topic to which the message should be published.
            - `payload` (dict): Payload of the message to send.
            - `from_uuid` (Optional[str], optional): UUID of the sender. Required for interception.
            - `to_uuid` (Optional[str], optional): UUID of the recipient. Required for interception.

        - **Description**:
            - Serializes the payload to JSON, checks it against the message interceptor (if any),
              and publishes the message to the specified topic if valid.
        """
        start_time = time.time()
        log = {
            "topic": topic,
            "payload": payload,
            "from_uuid": from_uuid,
            "to_uuid": to_uuid,
            "start_time": start_time,
            "consumption": 0,
        }
        message = json.dumps(payload, default=str)
        interceptor = self.message_interceptor
        is_valid: bool = True
        if interceptor is not None and (from_uuid is not None and to_uuid is not None):
            is_valid = await interceptor.forward.remote(  # type:ignore
                from_uuid, to_uuid, message
            )
        if is_valid:
            await self.client.publish(topic=topic, payload=message, qos=1)
            logger.info(f"Message sent to {topic}: {message}")
        else:
            logger.info(f"Message not sent to {topic}: {message} due to interceptor")
        log["consumption"] = time.time() - start_time
        self._log_list.append(log)

    async def start_listening(self):
        """
        Start the task for listening to incoming messages.

        - **Description**:
            - Starts a task that listens for incoming messages and puts them into the queue.
            - Only starts the task if the connection to the broker is active.
        """
        if await self.is_connected():
            self.receive_messages_task = asyncio.create_task(self.receive_messages())
        else:
            logger.error("Cannot start listening because not connected to the Broker.")

    async def stop(self):
        """
        Stop the listener and disconnect from the MQTT broker.

        - **Description**:
            - Cancels the receive_messages_task and ensures the MQTT broker connection is closed.
        """
        assert self.receive_messages_task is not None
        self.receive_messages_task.cancel()
        await asyncio.gather(self.receive_messages_task, return_exceptions=True)
        await self.disconnect()
