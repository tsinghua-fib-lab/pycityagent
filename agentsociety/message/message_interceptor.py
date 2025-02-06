import asyncio
import inspect
import logging
from abc import ABC, abstractmethod
from collections import defaultdict
from collections.abc import Callable, Sequence
from copy import deepcopy
from typing import Any, Optional, Union

import ray
from ray.util.queue import Queue

from ..configs import LLMRequestConfig
from ..llm import LLM
from ..utils.decorators import lock_decorator

DEFAULT_ERROR_STRING = """
From `{from_uuid}` To `{to_uuid}` abort due to block `{block_name}`
"""

logger = logging.getLogger("message_interceptor")

__all__ = [
    "MessageBlockBase",
    "MessageInterceptor",
    "MessageBlockListenerBase",
]


class MessageBlockBase(ABC):
    """
    用于过滤的block
    """

    def __init__(
        self,
        name: str = "",
    ) -> None:
        self._name = name
        self._llm = None
        self._lock = asyncio.Lock()

    @property
    def llm(
        self,
    ) -> LLM:
        if self._llm is None:
            raise RuntimeError(f"LLM access before assignment, please `set_llm` first!")
        return self._llm

    @property
    def name(
        self,
    ):
        return self._name

    @property
    def has_llm(
        self,
    ) -> bool:
        return self._llm is not None

    @lock_decorator
    async def set_llm(self, llm: LLM):
        """
        Set the llm_client of the block.
        """
        self._llm = llm

    @lock_decorator
    async def set_name(self, name: str):
        """
        Set the name of the block.
        """
        self._name = name

    @lock_decorator
    async def forward(
        self,
        from_uuid: str,
        to_uuid: str,
        msg: str,
        violation_counts: dict[str, int],
        black_list: list[tuple[str, str]],
    ) -> tuple[bool, str]:
        return True, ""


@ray.remote
class MessageInterceptor:
    """
    A class to intercept and process messages based on configured rules.
    """

    def __init__(
        self,
        blocks: Optional[list[MessageBlockBase]] = None,
        black_list: Optional[list[tuple[str, str]]] = None,
        llm_config: Optional[LLMRequestConfig] = None,
        queue: Optional[Queue] = None,
    ) -> None:
        """
        Initialize the MessageInterceptor with optional configuration.

        - **Args**:
            - `blocks` (Optional[list[MessageBlockBase]], optional): Initial list of message interception rules. Defaults to an empty list.
            - `black_list` (Optional[list[tuple[str, str]]], optional): Initial blacklist of communication pairs. Defaults to an empty list.
            - `llm_config` (Optional[LLMRequestConfig], optional): Configuration dictionary for initializing the LLM instance. Defaults to None.
            - `queue` (Optional[Queue], optional): Queue for message processing. Defaults to None.
        """
        if blocks is not None:
            self._blocks: list[MessageBlockBase] = blocks
        else:
            self._blocks: list[MessageBlockBase] = []
        self._violation_counts: dict[str, int] = defaultdict(int)
        if black_list is not None:
            self._black_list: list[tuple[str, str]] = black_list
        else:
            self._black_list: list[tuple[str, str]] = (
                []
            )  # list[tuple(from_uuid, to_uuid)] `None` means forbidden for everyone.
        if llm_config:
            self._llm = LLM(llm_config)
        else:
            self._llm = None
        self._queue = queue
        self._lock = asyncio.Lock()

    @property
    def llm(
        self,
    ) -> LLM:
        """
        Access the Large Language Model instance.

        - **Description**:
            - Provides access to the internal LLM instance. Raises an error if accessed before assignment.

        - **Raises**:
            - `RuntimeError`: If accessed before setting the LLM.

        - **Returns**:
            - `LLM`: The Large Language Model instance.
        """
        if self._llm is None:
            raise RuntimeError(f"LLM access before assignment, please `set_llm` first!")
        return self._llm

    @lock_decorator
    async def blocks(
        self,
    ) -> list[MessageBlockBase]:
        """
        Retrieve the message interception rules.

        - **Description**:
            - Returns a copy of the current list of message interception rules.

        - **Returns**:
            - `list[MessageBlockBase]`: The list of message interception rules.
        """
        return self._blocks

    @lock_decorator
    async def set_llm(self, llm: LLM):
        """
        Set the Large Language Model instance.

        - **Description**:
            - Updates the internal LLM instance used for message processing.

        - **Args**:
            - `llm` (LLM): The LLM instance to be set.

        - **Returns**:
            - `None`
        """
        if self._llm is None:
            self._llm = llm

    @lock_decorator
    async def violation_counts(
        self,
    ) -> dict[str, int]:
        """
        Retrieve the violation counts.

        - **Description**:
            - Returns a deep copy of the violation counts to prevent external modification of the original data.

        - **Returns**:
            - `dict[str, int]`: The dictionary of violation counts.
        """
        return deepcopy(self._violation_counts)

    @property
    def has_llm(
        self,
    ) -> bool:
        """
        Check if a Large Language Model is configured.

        - **Description**:
            - Confirms whether a Large Language Model instance has been set.

        - **Returns**:
            - `bool`: True if an LLM is set, otherwise False.
        """
        return self._llm is not None

    @lock_decorator
    async def black_list(
        self,
    ) -> list[tuple[str, str]]:
        """
        Retrieve the blacklist.

        - **Description**:
            - Returns a deep copy of the current blacklist to protect the original data from external modifications.

        - **Returns**:
            - `list[tuple[str, str]]`: The blacklist.
        """
        return deepcopy(self._black_list)

    @lock_decorator
    async def add_to_black_list(
        self, black_list: Union[list[tuple[str, str]], tuple[str, str]]
    ):
        """
        Add entries to the blacklist.

        - **Description**:
            - Adds one or more entries to the blacklist, ensuring each entry's uniqueness.

        - **Args**:
            - `black_list` (Union[list[tuple[str, str]], tuple[str, str]]):
                Can be a single tuple or a list of tuples indicating the entries to add to the blacklist.

        - **Returns**:
            - `None`
        """
        if all(isinstance(s, str) for s in black_list):
            # tuple[str,str]
            _black_list = [black_list]
        else:
            _black_list = black_list
        _black_list = [tuple(p) for p in _black_list]
        self._black_list.extend(_black_list)  # type: ignore
        self._black_list = list(set(self._black_list))

    @property
    def has_queue(
        self,
    ) -> bool:
        """
        Check if a queue is configured.

        - **Description**:
            - Confirms whether a queue instance has been set for message processing.

        - **Returns**:
            - `bool`: True if a queue is set, otherwise False.
        """
        return self._queue is not None

    @lock_decorator
    async def set_queue(self, queue: Queue):
        """
        Set the queue of the MessageInterceptor.

        - **Description**:
            - Assigns a queue to the MessageInterceptor for asynchronous message handling.

        - **Args**:
            - `queue` (Queue): The queue instance to be set.

        - **Returns**:
            - `None`
        """
        self._queue = queue

    @lock_decorator
    async def remove_from_black_list(
        self, to_remove_black_list: Union[list[tuple[str, str]], tuple[str, str]]
    ):
        """
        Remove entries from the blacklist.

        - **Description**:
            - Removes one or more entries from the blacklist, ensuring each entry's removal.

        - **Args**:
            - `to_remove_black_list` (Union[list[tuple[str, str]], tuple[str, str]]):
                Can be a single tuple or a list of tuples indicating the entries to remove from the blacklist.

        - **Returns**:
            - `None`
        """
        if all(isinstance(s, str) for s in to_remove_black_list):
            # tuple[str,str]
            _black_list = [to_remove_black_list]
        else:
            _black_list = to_remove_black_list
        _black_list_set = {tuple(p) for p in _black_list}
        self._black_list = [p for p in self._black_list if p not in _black_list_set]

    @property
    def queue(
        self,
    ) -> Queue:
        """
        Access the queue used for message processing.

        - **Description**:
            - Provides access to the internal queue. Raises an error if accessed before assignment.

        - **Raises**:
            - `RuntimeError`: If accessed before setting the queue.

        - **Returns**:
            - `Queue`: The queue instance.
        """
        if self._queue is None:
            raise RuntimeError(
                f"Queue access before assignment, please `set_queue` first!"
            )
        return self._queue

    @lock_decorator
    async def insert_block(self, block: MessageBlockBase, index: Optional[int] = None):
        """
        Insert a message block into the blocks list at a specified position.

        - **Description**:
            - Inserts a new message interception rule into the list at the specified index or appends it if no index is provided.

        - **Args**:
            - `block` (MessageBlockBase): The message block to insert.
            - `index` (Optional[int], optional): The position at which to insert the block. Defaults to appending at the end.

        - **Returns**:
            - `None`
        """
        if index is None:
            index = len(self._blocks)
        self._blocks.insert(index, block)

    @lock_decorator
    async def pop_block(self, index: Optional[int] = None) -> MessageBlockBase:
        """
        Remove and return a message block from the blocks list.

        - **Description**:
            - Removes and returns the message block at the specified index or the last one if no index is provided.

        - **Args**:
            - `index` (Optional[int], optional): The position of the block to remove. Defaults to removing the last element.

        - **Returns**:
            - `MessageBlockBase`: The removed message block.
        """
        if index is None:
            index = -1
        return self._blocks.pop(index)

    @lock_decorator
    async def set_black_list(
        self, black_list: Union[list[tuple[str, str]], tuple[str, str]]
    ):
        """
        Set the blacklist with new entries.

        - **Description**:
            - Updates the blacklist with new entries, ensuring each entry's uniqueness.

        - **Args**:
            - `black_list` (Union[list[tuple[str, str]], tuple[str, str]]):
                Can be a single tuple or a list of tuples indicating the new blacklist entries.

        - **Returns**:
            - `None`
        """
        if all(isinstance(s, str) for s in black_list):
            # tuple[str,str]
            _black_list = [black_list]
        else:
            _black_list = black_list
        _black_list = [tuple(p) for p in _black_list]
        self._black_list = list(set(_black_list))  # type: ignore

    @lock_decorator
    async def set_blocks(self, blocks: list[MessageBlockBase]):
        """
        Replace the current blocks list with a new list of message blocks.

        - **Description**:
            - Sets a new list of message interception rules, replacing the existing list.

        - **Args**:
            - `blocks` (list[MessageBlockBase]): The new list of message blocks to set.

        - **Returns**:
            - `None`
        """
        self._blocks = blocks

    @lock_decorator
    async def forward(
        self,
        from_uuid: str,
        to_uuid: str,
        msg: str,
    ):
        """
        Forward a message through all message blocks.

        - **Description**:
            - Processes a message by passing it through all configured message blocks. Each block can modify the message or prevent its forwarding based on implemented logic.

        - **Args**:
            - `from_uuid` (str): The UUID of the sender.
            - `to_uuid` (str): The UUID of the recipient.
            - `msg` (str): The message content to forward.

        - **Returns**:
            - `bool`: True if the message was successfully processed by all blocks, otherwise False.
        """
        for _block in self._blocks:
            if not _block.has_llm and self.has_llm:
                await _block.set_llm(self.llm)
            func_params = inspect.signature(_block.forward).parameters
            _args = {
                "from_uuid": from_uuid,
                "to_uuid": to_uuid,
                "msg": msg,
                "violation_counts": self._violation_counts,
                "black_list": self._black_list,
            }
            _required_args = {k: v for k, v in _args.items() if k in func_params}
            res = await _block.forward(**_required_args)
            try:
                is_valid, err = res
            except TypeError as e:
                is_valid: bool = res  # type:ignore
                err = (
                    DEFAULT_ERROR_STRING.format(
                        from_uuid=from_uuid,
                        to_uuid=to_uuid,
                        block_name=f"{_block.__class__.__name__} `{_block.name}`",
                    )
                    if not is_valid
                    else ""
                )
            if not is_valid:
                if self.has_queue:
                    logger.debug(f"put `{err}` into queue")
                    await self.queue.put_async(err)  # type:ignore
                self._violation_counts[from_uuid] += 1
                print(self._black_list)
                return False
            else:
                # valid
                pass
        print(self._black_list)
        return True


class MessageBlockListenerBase(ABC):
    """
    Base class for message block listeners that can listen to a queue and process items.

    - **Attributes**:
        - `_queue` (Optional[Queue]): Queue from which the listener retrieves items.
        - `_lock` (asyncio.Lock): Lock for thread-safe access in asynchronous environments.
        - `_values_from_queue` (list[Any]): List of values retrieved from the queue if saving is enabled.
        - `_save_queue_values` (bool): Flag indicating whether to save values from the queue.
        - `_get_queue_period` (float): Period in seconds between queue retrieval attempts.
    """

    def __init__(
        self,
        save_queue_values: bool = False,
        get_queue_period: float = 0.1,
    ) -> None:
        """
        Initialize the MessageBlockListenerBase with optional configuration.

        - **Args**:
            - `save_queue_values` (bool, optional): Whether to save values retrieved from the queue. Defaults to False.
            - `get_queue_period` (float, optional): Time period in seconds between queue retrieval attempts. Defaults to 0.1.
        """
        self._queue = None
        self._lock = asyncio.Lock()
        self._values_from_queue: list[Any] = []
        self._save_queue_values = save_queue_values
        self._get_queue_period = get_queue_period

    @property
    def queue(
        self,
    ) -> Queue:
        """
        Access the queue used by the listener.

        - **Description**:
            - Provides access to the internal queue. Raises an error if accessed before assignment.

        - **Raises**:
            - `RuntimeError`: If accessed before setting the queue.

        - **Returns**:
            - `Queue`: The queue instance.
        """
        if self._queue is None:
            raise RuntimeError(
                f"Queue access before assignment, please `set_queue` first!"
            )
        return self._queue

    @property
    def has_queue(
        self,
    ) -> bool:
        """
        Check if a queue is configured.

        - **Description**:
            - Confirms whether a queue instance has been set for the listener.

        - **Returns**:
            - `b
        """
        return self._queue is not None

    @lock_decorator
    async def set_queue(self, queue: Queue):
        """
        Set the queue for the listener.

        - **Description**:
            - Assigns a queue to the listener for asynchronous item processing.

        - **Args**:
            - `queue` (Queue): The queue instance to be set.

        - **Returns**:
            - `None`
        """
        self._queue = queue

    @lock_decorator
    async def forward(
        self,
    ):
        """
        Continuously retrieve items from the queue and process them.

        - **Description**:
            - Listens to the queue, retrieves items at intervals defined by `_get_queue_period`,
              and processes each item. If `_save_queue_values` is True, it saves the items in `_values_from_queue`.

        - **Returns**:
            - `None`
        """
        while True:
            if self.has_queue:
                value = await self.queue.get_async()  # type: ignore
                if self._save_queue_values:
                    self._values_from_queue.append(value)
                logger.debug(f"get `{value}` from queue")
                # do something with the value
            await asyncio.sleep(self._get_queue_period)
