"""
Base class of memory
"""

import logging
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Sequence, Tuple, Union

from .memory_unit import MemoryUnit


class MemoryBase(ABC):
    """
    Abstract base class for memory management.

    This class provides a framework for managing memory units. It defines methods that must be implemented by subclasses
    to handle adding, removing, loading, and resetting memory units.
    """

    def __init__(self) -> None:
        """
        Initializes the MemoryBase instance.

        Attributes:
            _memories (Dict[MemoryUnit, Dict]): A dictionary to store memory units and their associated data.
        """
        self._memories: Dict[MemoryUnit, Dict] = {}

    @abstractmethod
    def add(self, msg: Union[MemoryUnit, Sequence[MemoryUnit]]) -> None:
        """
        Adds one or more memory units to the memory.

        Args:
            msg (Union[MemoryUnit, Sequence[MemoryUnit]]): A single memory unit or a sequence of memory units to add.
        """
        raise NotImplementedError

    @abstractmethod
    def pop(self, index: int) -> MemoryUnit:
        """
        Removes and returns the memory unit at the specified index.

        Args:
            index (int): The index of the memory unit to remove.

        Returns:
            MemoryUnit: The removed memory unit.
        """
        pass

    @abstractmethod
    def load(
        self, msg: Union[MemoryUnit, Sequence[MemoryUnit]], reset_memory: bool = False
    ) -> None:
        """
        Loads one or more memory units into the memory.

        Args:
            msg (Union[MemoryUnit, Sequence[MemoryUnit]]): A single memory unit or a sequence of memory units to load.
            reset_memory (bool, optional): If True, clears the existing memory before loading new units. Defaults to False.
        """
        raise NotImplementedError

    @abstractmethod
    def reset(self) -> None:
        """
        Resets the memory, clearing all stored memory units.
        """
        raise NotImplementedError

    def _fetch_recent_memory(
        self, recent_n: Optional[int] = None
    ) -> Sequence[MemoryUnit]:
        """
        Fetches the most recent memory units.

        Args:
            recent_n (Optional[int], optional): The number of recent memory units to fetch. If None, returns all memory units. Defaults to None.

        Returns:
            Sequence[MemoryUnit]: A sequence of the most recent memory units, up to `recent_n`.

        Raises:
            logging.Warning: Logs a warning if the requested number of recent memory units (`recent_n`) is greater than the total number of memory units available.
        """
        _memories = self._memories
        _list_units = list(_memories.keys())
        if recent_n is None:
            return _list_units
        if len(_memories) < recent_n:
            logging.warning(
                f"Length of memory {len(_memories)} is less than recent_n {recent_n}, returning all available memories."
            )
        return _list_units[-recent_n:]
