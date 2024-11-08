import logging
from copy import deepcopy
from typing import Any, Dict, List, Literal, Optional, Sequence, Tuple, Union

from .const import *
from .profile import ProfileMemory
from .self_define import DynamicMemory
from .state import StateMemory


class Memory:
    def __init__(self, config: Optional[Dict[Any, Any]] = None) -> None:
        self._state = StateMemory()
        self._profile = ProfileMemory()
        _dynamic_config: Dict[Any, Any] = {}
        if config is not None:
            for k, v in config.items():
                try:
                    _type, _value = v
                except TypeError as e:
                    _value = v()
                if k in PROFILE_ATTRIBUTES or k in STATE_ATTRIBUTES:
                    logging.warning(f"key `{k}` already declared in memory!")
                    continue
                _dynamic_config[k] = deepcopy(_value)
        self._dynamic = DynamicMemory(required_attributes=_dynamic_config)

    def get(
        self,
        key: Any,
        mode: Union[Literal["read only"], Literal["read and write"]] = "read only",
    ):
        if mode == "read only":
            process_func = deepcopy
        elif mode == "read and write":
            process_func = lambda x: x
        else:
            raise ValueError(f"Invalid get mode `{mode}`!")
        for _mem in [self._state, self._profile, self._dynamic]:
            try:
                value = _mem.get(key)
                return process_func(value)
            except KeyError as e:
                continue
        raise AttributeError(f"No attribute `{key}` in memories!")

    def update(
        self,
        key: Any,
        value: Any,
        mode: Union[Literal["replace"], Literal["merge"]] = "replace",
    ):
        for _mem in [self._state, self._profile, self._dynamic]:
            try:
                _ = _mem.get(key)
            except KeyError as e:
                continue
            # read and write
            original_value = _mem.get(key)
            if mode == "replace":
                _mem.update(key, value)
            elif mode == "merge":
                if isinstance(original_value, set):
                    original_value.update(set(value))
                elif isinstance(original_value, dict):
                    original_value.update(dict(value))
                elif isinstance(original_value, list):
                    original_value.extend(list(value))
                else:
                    logging.warning(
                        f"Type of {type(original_value)} does not support mode `merge`, using `replace` instead!"
                    )
                    _mem.update(key, value)
            else:
                raise ValueError(f"Invalid update mode `{mode}`!")
            return
        raise AttributeError(f"No attribute `{key}` in memories!")

    def update_batch(
        self,
        content: Dict,
        mode: Union[Literal["replace"], Literal["merge"]] = "replace",
    ):
        for k, v in content.items():
            self.update(k, v, mode)
