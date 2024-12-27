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

logger = logging.getLogger("pycityagent")


class MemoryUnit:
    def __init__(
        self,
        content: Optional[dict] = None,
        required_attributes: Optional[dict] = None,
        activate_timestamp: bool = False,
    ) -> None:
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
        await self._lock.acquire()
        self._content = {}
        self._lock.release()

    async def top_k_values(
        self,
        key: Any,
        metric: Callable[[Any], Any],
        top_k: Optional[int] = None,
        preserve_order: bool = True,
    ) -> Union[Sequence[Any], Any]:
        await self._lock.acquire()
        values = self._content[key]
        if not isinstance(values, Sequence):
            logger.warning(
                f"the value stored in key `{key}` is not `sequence`, return value `{values}` instead!"
            )
            return values
        else:
            _values_with_idx = [(i, v) for i, v in enumerate(values)]
            _sorted_values_with_idx = sorted(
                _values_with_idx, key=lambda i_v: -metric(i_v[1])
            )
            top_k = len(values) if top_k is None else top_k
            if len(_sorted_values_with_idx) < top_k:
                logger.debug(
                    f"Length of values {len(_sorted_values_with_idx)} is less than top_k {top_k}, returning all values."
                )
            self._lock.release()
            if preserve_order:
                return [
                    i_v[1]
                    for i_v in sorted(
                        _sorted_values_with_idx[:top_k], key=lambda i_v: i_v[0]
                    )
                ]
            else:
                return [i_v[1] for i_v in _sorted_values_with_idx[:top_k]]

    async def dict_values(
        self,
    ) -> dict[Any, Any]:
        return self._content


class MemoryBase(ABC):

    def __init__(self) -> None:
        self._memories: dict[Any, dict] = {}
        self._lock = asyncio.Lock()

    @abstractmethod
    async def add(self, msg: Union[Any, Sequence[Any]]) -> None:
        raise NotImplementedError

    @abstractmethod
    async def pop(self, index: int) -> Any:
        pass

    @abstractmethod
    async def load(
        self, snapshots: Union[Any, Sequence[Any]], reset_memory: bool = False
    ) -> None:
        raise NotImplementedError

    @abstractmethod
    async def export(
        self,
    ) -> Sequence[Any]:
        raise NotImplementedError

    @abstractmethod
    async def reset(self) -> None:
        raise NotImplementedError

    def _fetch_recent_memory(self, recent_n: Optional[int] = None) -> Sequence[Any]:
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
        raise NotImplementedError

    @abstractmethod
    async def update(self, key: Any, value: Any, store_snapshot: bool):
        raise NotImplementedError

    def __getitem__(self, index: Any) -> Any:
        return list(self._memories.keys())[index]
