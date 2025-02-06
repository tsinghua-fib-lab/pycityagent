"""
Base class of memory
"""

import asyncio
import logging
import time
from abc import ABC, abstractmethod
from collections.abc import Callable, Sequence
from typing import Any, Optional, Union

from .const import *

logger = logging.getLogger("agentsociety")


class MemoryUnit:
    """
    A class used to manage a unit of memory that can be updated asynchronously.

    - **Description**:
        - This class allows for the storage of content within a dictionary-like structure,
          with optional required attributes and timestamp tracking. It provides methods to
          safely update or clear the stored content using an internal lock to prevent race conditions.

    - **Attributes**:
        - `_content`: Internal dictionary storing the content of the memory unit.
        - `_lock`: An asyncio Lock object used to ensure thread-safe operations on `_content`.
        - `_activate_timestamp`: Boolean flag indicating whether to track changes with timestamps.
    """

    def __init__(
        self,
        content: Optional[dict] = None,
        required_attributes: Optional[dict] = None,
        activate_timestamp: bool = False,
    ) -> None:
        """
        Initialize a new instance of MemoryUnit.

        - **Args**:
            - `content` (Optional[Dict[Any, Any]], optional): Initial content to store in the memory unit. Defaults to an empty dictionary.
            - `required_attributes` (Optional[Dict[Any, Any]], optional): Attributes that must be present in the memory unit. Defaults to None.
            - `activate_timestamp` (bool, optional): Whether to track changes with timestamps. Defaults to False.
        """
        self._content = {}
        self._lock = asyncio.Lock()
        self._activate_timestamp = activate_timestamp
        if required_attributes is not None:
            self._content.update(required_attributes)
        if content is not None:
            self._content.update(content)
        if activate_timestamp and TIME_STAMP_KEY not in self._content:
            self._content[TIME_STAMP_KEY] = time.time()
        for _prop, _value in self._content.items():
            self._set_attribute(_prop, _value)

    def __getitem__(self, key: Any) -> Any:
        return self._content[key]

    def _create_property(self, property_name: str, property_value: Any):

        def _getter(self):
            return getattr(self, f"{SELF_DEFINE_PREFIX}{property_name}", None)

        def _setter(self, value):
            setattr(self, f"{SELF_DEFINE_PREFIX}{property_name}", value)

        setattr(self.__class__, property_name, property(_getter, _setter))
        setattr(self, f"{SELF_DEFINE_PREFIX}{property_name}", property_value)

    def _set_attribute(self, property_name: str, property_value: Any):
        if not hasattr(self, f"{SELF_DEFINE_PREFIX}{property_name}"):
            self._create_property(property_name, property_value)
        else:
            setattr(self, f"{SELF_DEFINE_PREFIX}{property_name}", property_value)

    async def update(self, content: dict) -> None:
        """
        Update the memory unit's content with the provided dictionary, respecting type consistency.

        - **Args**:
            - `content` (Dict[Any, Any]): A dictionary containing the updates to apply.

        - **Notes**:
            - If `activate_timestamp` is True, the timestamp will be updated after the operation.
            - Type warnings are logged when the type of a value changes.
        """
        await self._lock.acquire()
        for k, v in content.items():
            if k in self._content:
                orig_v = self._content[k]
                orig_type, new_type = type(orig_v), type(v)
                if not orig_type == new_type:
                    logger.debug(
                        f"Type warning: The type of the value for key '{k}' is changing from `{orig_type.__name__}` to `{new_type.__name__}`!"
                    )
        self._content.update(content)
        for _prop, _value in self._content.items():
            self._set_attribute(_prop, _value)
        if self._activate_timestamp:
            self._set_attribute(TIME_STAMP_KEY, time.time())
        self._lock.release()

    async def clear(self) -> None:
        """
        Clear all content from the memory unit.
        """
        await self._lock.acquire()
        self._content = {}
        self._lock.release()

    # async def top_k_values(
    #     self,
    #     key: Any,
    #     metric: Callable[[Any], Any],
    #     top_k: Optional[int] = None,
    #     preserve_order: bool = True,
    # ) -> Union[Sequence[Any], Any]:
    #     await self._lock.acquire()
    #     values = self._content[key]
    #     if not isinstance(values, Sequence):
    #         logger.warning(
    #             f"the value stored in key `{key}` is not `sequence`, return value `{values}` instead!"
    #         )
    #         return values
    #     else:
    #         _values_with_idx = [(i, v) for i, v in enumerate(values)]
    #         _sorted_values_with_idx = sorted(
    #             _values_with_idx, key=lambda i_v: -metric(i_v[1])
    #         )
    #         top_k = len(values) if top_k is None else top_k
    #         if len(_sorted_values_with_idx) < top_k:
    #             logger.debug(
    #                 f"Length of values {len(_sorted_values_with_idx)} is less than top_k {top_k}, returning all values."
    #             )
    #         self._lock.release()
    #         if preserve_order:
    #             return [
    #                 i_v[1]
    #                 for i_v in sorted(
    #                     _sorted_values_with_idx[:top_k], key=lambda i_v: i_v[0]
    #                 )
    #             ]
    #         else:
    #             return [i_v[1] for i_v in _sorted_values_with_idx[:top_k]]

    async def dict_values(
        self,
    ) -> dict[Any, Any]:
        """
        Return the dict value of the memory unit.
        """
        return self._content


class MemoryBase(ABC):
    """
    An abstract base class for managing a memory system.

    This class defines the interface for adding, popping, loading, exporting,
    and resetting memory items. It also includes methods for fetching recent
    memories and interacting with specific memory entries.
    """

    def __init__(self) -> None:
        """
        Initialize a new instance of MemoryBase.

        - **Attributes**:
            - `_memories`: A dictionary that stores memory items.
            - `_lock`: An asyncio Lock object to ensure thread-safe operations on `_memories`.
        """
        self._memories: dict[Any, dict] = {}
        self._lock = asyncio.Lock()

    @abstractmethod
    async def add(self, msg: Union[Any, Sequence[Any]]) -> None:
        """
        Add one or more items to the memory.

        - **Args**:
            - `msg` (Union[Any, Sequence[Any]]): The item or sequence of items to add.
        """
        raise NotImplementedError

    @abstractmethod
    async def pop(self, index: int) -> Any:
        """
        Remove and return an item from the memory at the specified index.

        - **Args**:
            - `index` (int): The index of the item to remove.
        """
        pass

    @abstractmethod
    async def load(
        self, snapshots: Union[Any, Sequence[Any]], reset_memory: bool = False
    ) -> None:
        """
        Load one or more snapshots into the memory.

        - **Args**:
            - `snapshots` (Union[Any, Sequence[Any]]): The snapshot(s) to load.
            - `reset_memory` (bool, optional): Whether to clear existing memory before loading. Defaults to False.
        """
        raise NotImplementedError

    @abstractmethod
    async def export(
        self,
    ) -> Sequence[Any]:
        """
        Export all items currently stored in the memory.

        - **Returns**:
            - `Sequence[Any]`: A sequence of memory items.
        """
        raise NotImplementedError

    @abstractmethod
    async def reset(self) -> None:
        """
        Reset the memory by clearing all items.
        """
        raise NotImplementedError

    def _fetch_recent_memory(self, recent_n: Optional[int] = None) -> Sequence[Any]:
        """
        Fetch the most recent N memory entries.

        - **Args**:
            - `recent_n` (Optional[int], optional): The number of recent entries to fetch. If not provided, returns all available entries.

        - **Returns**:
            - `Sequence[Any]`: A sequence of recent memory keys.
        """
        _memories = self._memories
        _list_units = list(_memories.keys())
        if recent_n is None:
            return _list_units
        if len(_memories) < recent_n:
            logger.debug(
                f"Length of memory {len(_memories)} is less than recent_n {recent_n}, returning all available memories."
            )
        return _list_units[-recent_n:]

    # interact
    @abstractmethod
    async def get(self, key: Any):
        """
        Retrieve an item from the memory by its key.

        - **Args**:
            - `key` (Any): The key of the item to retrieve.

        - **Returns**:
            - `Any`: The retrieved memory item.
        """
        raise NotImplementedError

    @abstractmethod
    async def update(self, key: Any, value: Any, store_snapshot: bool):
        """
        Update an existing item in the memory with a new value.

        - **Args**:
            - `key` (Any): The key of the item to update.
            - `value` (Any): The new value for the item.
            - `store_snapshot` (bool): Whether to store a snapshot after updating.
        """
        raise NotImplementedError

    def __getitem__(self, index: Any) -> Any:
        return list(self._memories.keys())[index]
