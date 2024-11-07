"""
Self Define Data
"""

from typing import Any, Dict, List, Optional, Sequence, Tuple, Union

from .memory_base import MemoryBase
from .memory_unit import MemoryUnit
from .utils import convert_msg_to_sequence


class DynamicMemory(MemoryBase):
    """
    A dynamic memory management class that allows for the storage and manipulation of arbitrary properties.

    This class extends `MemoryBase` and provides methods to dynamically create, set, and retrieve properties.
    It also supports storing these properties in memory units.
    """

    PREFIX = "self_define_"

    def __init__(
        self, properties: Dict[str, Any], store_property_in_memory: bool = False
    ) -> None:
        """
        Initializes the DynamicMemory instance.

        Args:
            properties (Dict[str, Any]): A dictionary of initial properties to set.
            store_property_in_memory (bool, optional): If True, stores the initial properties in memory. Defaults to False.
        """
        super().__init__()
        for _prop, _value in properties.items():
            self._set_attribute(_prop, _value)
        if store_property_in_memory:
            self.add(msg=MemoryUnit(self._get_attributes_dict()))

    def add(self, msg: Union[MemoryUnit, Sequence[MemoryUnit]]) -> None:
        """
        Adds one or more memory units to the memory.

        Args:
            msg (Union[MemoryUnit, Sequence[MemoryUnit]]): A single memory unit or a sequence of memory units to add.
        """
        _memories = self._memories
        msg = convert_msg_to_sequence(msg)
        for unit in msg:
            if unit not in _memories:
                _memories[unit] = {}

    def pop(self, index: int) -> MemoryUnit:
        """
        Removes and returns the memory unit at the specified index.

        Args:
            index (int): The index of the memory unit to remove.

        Returns:
            MemoryUnit: The removed memory unit.

        Raises:
            ValueError: If the index is out of range.
        """
        _memories = self._memories
        try:
            pop_unit = list(_memories.keys())[index]
            _memories.pop(pop_unit)
            return pop_unit
        except IndexError as e:
            raise ValueError(f"Index {index} not in memory!")

    def load(
        self, msg: Union[MemoryUnit, Sequence[MemoryUnit]], reset_memory: bool = False
    ) -> None:
        """
        Loads one or more memory units into the memory.

        Args:
            msg (Union[MemoryUnit, Sequence[MemoryUnit]]): A single memory unit or a sequence of memory units to load.
            reset_memory (bool, optional): If True, clears the existing memory before loading new units. Defaults to False.
        """
        if reset_memory:
            self.reset()
        self.add(msg)

    def reset(self) -> None:
        """
        Resets the memory, clearing all stored memory units.
        """
        self._memories = {}

    def _create_property(self, property_name: str, property_value: Any) -> None:
        """
        Creates a dynamic property for the given name and value.

        Args:
            property_name (str): The name of the property to create.
            property_value (Any): The initial value of the property.
        """

        def _getter(self):
            return getattr(self, f"{self.PREFIX}{property_name}", None)

        def _setter(self, value):
            setattr(self, f"{self.PREFIX}{property_name}", value)

        setattr(self.__class__, property_name, property(_getter, _setter))
        setattr(self, f"{self.PREFIX}{property_name}", property_value)

    def _set_attribute(self, property_name: str, property_value: Any) -> None:
        """
        Sets the value of a property, creating it if it does not exist.

        Args:
            property_name (str): The name of the property to set.
            property_value (Any): The value to assign to the property.
        """
        if not hasattr(self, f"{self.PREFIX}{property_name}"):
            self._create_property(property_name, property_value)
        else:
            setattr(self, f"{self.PREFIX}{property_name}", property_value)

    def _get_attributes_dict(self) -> Dict[str, Any]:
        """
        Retrieves a dictionary of all dynamically created properties.

        Returns:
            Dict[str, Any]: A dictionary containing the names and values of all dynamically created properties.
        """
        attributes: Dict[str, Any] = {}
        for key in self.__dict__:
            if key.startswith(self.PREFIX):
                attr_name = key[len(self.PREFIX) :]
                attributes[attr_name] = getattr(self, attr_name)
        return attributes

    def update_property(
        self, properties: Dict[str, Any], store_property_in_memory: bool = False
    ) -> None:
        """
        Updates the values of existing properties or creates new ones.

        Args:
            properties (Dict[str, Any]): A dictionary of properties to update or create.
            store_property_in_memory (bool, optional): If True, stores the updated properties in memory. Defaults to False.
        """
        for _prop, _value in properties.items():
            self._set_attribute(_prop, _value)
        if store_property_in_memory:
            self.add(msg=MemoryUnit(self._get_attributes_dict()))
