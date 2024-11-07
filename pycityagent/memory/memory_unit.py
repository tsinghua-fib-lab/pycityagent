from typing import Any, Dict, Optional


class MemoryUnit:
    """
    Represents a unit of memory with a dictionary to store content.

    This class allows for the storage and manipulation of memory content using a dictionary.
    Each item in the dictionary can be accessed as an attribute of the instance, dynamically created based on the content.
    """

    PREFIX = "self_define_"

    def __init__(self, content: Optional[Dict] = None) -> None:
        """
        Initializes a MemoryUnit instance.

        Args:
            content (Optional[Dict], optional): Initial content to be stored in the memory unit. Defaults to None.
        """
        self._content = {}
        if content is not None:
            self._content.update(content)
        for _prop, _value in self._content.items():
            self._set_attribute(_prop, _value)

    def __getitem__(self, key: Any) -> Any:
        """
        Retrieves the value associated with the given key from the memory unit's content.

        Args:
            key (Any): The key to look up in the content.

        Returns:
            Any: The value associated with the key.

        Raises:
            KeyError: If the key is not found in the content.
        """
        return self._content[key]

    def _create_property(self, property_name: str, property_value: Any):
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

    def _set_attribute(self, property_name: str, property_value: Any):
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

    def update(self, content: Dict) -> None:
        """
        Updates the memory unit's content with the provided dictionary.

        Args:
            content (Dict): A dictionary containing key-value pairs to update the content.
        """
        self._content.update(content)
        for _prop, _value in self._content.items():
            self._set_attribute(_prop, _value)

    def clear(self) -> None:
        """
        Clears all content from the memory unit, including any dynamically created properties.
        """
        for _prop, _ in self._content.items():
            delattr(self, f"{self.PREFIX}{_prop}")
        self._content = {}
