from typing import Any, Callable, Dict, List, Optional, Union
from ..memory import Memory
from .tool import Tool

class Context:
    """
    A class to manage the context for tools and memory.

    Attributes:
        memory (Optional[Memory]): An optional memory instance bound to the context.
        input_keys (List[Union[str, Dict[str, Tool]]]): A list of input keys or tools.
        temp_keys (List[str]): A list of temporary keys.
        update_keys (List[str]): A list of keys to be updated.
        temp (Dict[str, Any]): A dictionary to store temporary values.
        update (Dict[str, Any]): A dictionary to store updated values.
    """
    
    def __init__(self, input_keys: List[Union[str, Dict[str, Tool]]], temp_keys: Optional[List[str]] = None, update_keys: Optional[List[str]] = None) -> None:
        """
        Initializes the Context with input keys, optional temporary keys, and optional update keys.

        Args:
            input_keys (List[Union[str, Dict[str, Tool]]]): A list of input keys or tools.
            temp_keys (Optional[List[str]]): A list of temporary keys. Defaults to an empty list.
            update_keys (Optional[List[str]]): A list of keys to be updated. Defaults to an empty list.
        """
        self.memory: Optional[Memory] = None
        self.input_keys = input_keys
        self.temp_keys = temp_keys if temp_keys else []
        self.update_keys = update_keys if update_keys else []
        self.temp: Dict[str, Any] = {}

    async def get(self, key: str) -> Any:
        """
        Retrieves the value associated with the given key from the context.

        Args:
            key (str): The key for which to retrieve the associated value.

        Returns:
            Any: The value associated with the key.

        Raises:
            KeyError: If the key is not found in the input keys or memory.
        """
        for item in self.input_keys:
            if isinstance(item, str) and item == key:
                if self.memory:
                    try:
                        return self.memory.get(key)
                    except KeyError:
                        raise KeyError(f"Input key '{key}' not found in memory.")
            elif isinstance(item, dict) and key in item:
                tool = item[key]
                return await tool()
        raise KeyError(f"Key '{key}' not found in input keys.")
    
    def update(self, key: str, value: Any) -> None:
        """
        Updates the value in memory associated with the given key.
        Args:
            key (str): The key to be updated.
            value (Any): The new value to associate with the key.

        Raises:
            ValueError: If the memory is not bound to the context.
        """
        if self.memory:
            self.memory.update(key, value)
        else:
            raise ValueError("Memory is not bound to the context.")

    async def resolve(self, key: Union[str, Tool]) -> Any:
        """
        Resolves the given key to its value, either by retrieving it
        or by invoking the associated Tool.

        Args:
            key (Union[str, Tool]): The key to resolve, either a string or a Tool instance.

        Returns:
            Any: The resolved value.

        Raises:
            ValueError: If the key is neither a string nor a Tool instance.
        """
        if isinstance(key, str):
            return await self.get(key)
        elif isinstance(key, Tool):
            return await key()
        else:
            raise ValueError("Key must be either a string or a Tool instance.")