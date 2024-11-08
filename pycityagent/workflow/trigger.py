import asyncio
from typing import Any, Callable, Dict, List, Optional, Union
import socket
from ..memory import Memory
    
class EventTrigger:
    """Base class for event triggers that wait for specific conditions to be met."""
    
    async def wait_for_trigger(self) -> None:
        """Wait for the event trigger to be activated.
        
        Raises:
            NotImplementedError: Subclasses must implement this method.
        """
        raise NotImplementedError
    
class MemoryChangeTrigger(EventTrigger):
    """Event trigger that activates when a specific key in memory changes."""
    
    def __init__(self, memory: Memory, key: str) -> None:
        """Initialize the memory change trigger.

        Args:
            memory (Memory): The memory object to watch.
            key (str): The key in memory to monitor for changes.
        """
        self.memory = memory
        self.key = key
        self.trigger_event = asyncio.Event()
        self.memory.add_watcher(key, self.trigger_event.set)

    async def wait_for_trigger(self) -> None:
        """Wait for the memory change trigger to be activated."""
        await self.trigger_event.wait()
        self.trigger_event.clear()

class PortMessageTrigger(EventTrigger):
    """Event trigger that activates upon receiving a message on a specified UDP port."""
    
    def __init__(self, port: int) -> None:
        """Initialize the port message trigger.

        Args:
            port (int): The UDP port to listen for incoming messages.
        """
        self.port = port
        self.trigger_event = asyncio.Event()
        self.message: Optional[str] = None
        asyncio.create_task(self._listen_on_port())

    async def _listen_on_port(self) -> None:
        """Listen for incoming UDP messages on the specified port.

        Activates the trigger event when a message is received.
        """
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.bind(("", self.port))
            while True:
                data, _ = s.recvfrom(1024)
                self.message = data.decode()
                self.trigger_event.set()

    async def wait_for_trigger(self) -> None:
        """Wait for the port message trigger to be activated."""
        await self.trigger_event.wait()
        self.trigger_event.clear()