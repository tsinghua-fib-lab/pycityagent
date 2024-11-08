import logging
from copy import deepcopy
from typing import Any, Dict, List, Literal, Optional, Sequence, Tuple, Union, Callable

from .const import *
from .profile import ProfileMemory
from .self_define import DynamicMemory
from .state import StateMemory
import asyncio


class Memory:
    """
    A class to manage different types of memory (state, profile, dynamic).

    Attributes:
        _state (StateMemory): Stores state-related data.
        _profile (ProfileMemory): Stores profile-related data.
        _dynamic (DynamicMemory): Stores dynamically configured data.
    """

    def __init__(self, config: Optional[Dict[Any, Any]] = None) -> None:
        """
        Initializes the Memory with optional configuration.

        Args:
            config (Optional[Dict[Any, Any]], optional):
                A configuration dictionary for dynamic memory. The dictionary format is:
                - Key: The name of the dynamic memory field.
                - Value: Can be one of two formats:
                    1. A tuple where the first element is a variable type (e.g., int, str, etc.), and the second element is the default value for this field.
                    2. A callable that returns the default value when invoked (useful for complex default values).
                Note: If a key in `config` overlaps with predefined attributes in `PROFILE_ATTRIBUTES` or `STATE_ATTRIBUTES`, a warning will be logged, and the key will be ignored.
                Defaults to None.
        """
        self._state = StateMemory()
        self._profile = ProfileMemory()
        self.watchers: Dict[str, List[Callable]] = {}
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
    ) -> Any:
        """
        Retrieves a value from memory based on the given key and access mode.

        Args:
            key (Any): The key of the item to retrieve.
            mode (Union[Literal["read only"], Literal["read and write"]], optional): Access mode for the item. Defaults to "read only".

        Returns:
            Any: The value associated with the key.

        Raises:
            ValueError: If an invalid mode is provided.
            AttributeError: If the key is not found in any of the memory sections.
        """
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
    ) -> None:
        """
        Updates an existing value in the memory with a new value based on the given key and update mode.

        Args:
            key (Any): The key of the item to update.
            value (Any): The new value to set.
            mode (Union[Literal["replace"], Literal["merge"]], optional): Update mode. Defaults to "replace".

        Raises:
            ValueError: If an invalid update mode is provided.
            AttributeError: If the key is not found in any of the memory sections.
        """
        for _mem in [self._state, self._profile, self._dynamic]:
            try:
                _ = _mem.get(key)
            except KeyError as e:
                continue
            # read and write
            original_value = _mem.get(key)
            if mode == "replace":
                _mem.update(key, value)
                if key in self.watchers:
                    for callback in self.watchers[key]:
                        asyncio.create_task(callback())
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
                if key in self.watchers:
                    for callback in self.watchers[key]:
                        asyncio.create_task(callback())
            else:
                raise ValueError(f"Invalid update mode `{mode}`!")
            return
        raise AttributeError(f"No attribute `{key}` in memories!")

    def update_batch(
        self,
        content: Union[Dict, Sequence[Tuple[Any, Any]]],
        mode: Union[Literal["replace"], Literal["merge"]] = "replace",
    ) -> None:
        """
        Updates multiple values in the memory at once.

        Args:
            content (Union[Dict, Sequence[Tuple[Any, Any]]]): A dictionary or sequence of tuples containing the keys and values to update.
            mode (Union[Literal["replace"], Literal["merge"]], optional): Update mode. Defaults to "replace".

        Raises:
            TypeError: If the content type is neither a dictionary nor a sequence of tuples.
        """
        if isinstance(content, dict):
            for k, v in content.items():
                self.update(k, v, mode)
        elif isinstance(content, Sequence):
            for k, v in content:
                self.update(k, v, mode)
        else:
            raise TypeError(f"Invalid content type `{type(content)}`!")
        
    def add_watcher(self, key: str, callback: Callable) -> None:
        """
        Adds a callback function to be invoked when the value 
        associated with the specified key in memory is updated.
        
        Args:
            key (str): The key for which the watcher is being registered.
            callback (Callable): A callable function that will be executed 
            whenever the value associated with the specified key is updated.

        Notes:
            If the key does not already have any watchers, it will be 
            initialized with an empty list before appending the callback.
        """
        if key not in self.watchers:
            self.watchers[key] = []
        self.watchers[key].append(callback)
