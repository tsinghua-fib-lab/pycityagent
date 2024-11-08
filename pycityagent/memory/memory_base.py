"""
Base class of memory
"""

import logging
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Sequence, Tuple, Union

from .const import *


class MemoryUnit:
    def __init__(
        self, content: Optional[Dict] = None, required_attributes: Optional[Dict] = None
    ) -> None:
        self._content = {}
        if required_attributes is not None:
            self._content.update(required_attributes)
        if content is not None:
            self._content.update(content)
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

    def update(self, content: Dict) -> None:
        self._content.update(content)
        for _prop, _value in self._content.items():
            self._set_attribute(_prop, _value)

    def clear(self) -> None:
        for _prop, _ in self._content.items():
            delattr(self, f"{SELF_DEFINE_PREFIX}{_prop}")
        self._content = {}


class MemoryBase(ABC):

    def __init__(self) -> None:
        self._memories: Dict[Any, Dict] = {}

    @abstractmethod
    def add(self, msg: Union[Any, Sequence[Any]]) -> None:
        raise NotImplementedError

    @abstractmethod
    def pop(self, index: int) -> Any:
        pass

    @abstractmethod
    def load(self, msg: Union[Any, Sequence[Any]], reset_memory: bool = False) -> None:
        raise NotImplementedError

    @abstractmethod
    def reset(self) -> None:
        raise NotImplementedError

    def _fetch_recent_memory(self, recent_n: Optional[int] = None) -> Sequence[Any]:
        _memories = self._memories
        _list_units = list(_memories.keys())
        if recent_n is None:
            return _list_units
        if len(_memories) < recent_n:
            logging.warning(
                f"Length of memory {len(_memories)} is less than recent_n {recent_n}, returning all available memories."
            )
        return _list_units[-recent_n:]

    # interact
    @abstractmethod
    def get(self, key: Any):
        raise NotImplementedError

    @abstractmethod
    def update(self, key: Any, value: Any):
        raise NotImplementedError

    def __getitem__(self, index: Any) -> Any:
        return list(self._memories.keys())[index]
