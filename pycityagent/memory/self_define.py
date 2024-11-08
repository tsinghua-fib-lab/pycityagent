"""
Self Define Data
"""

from copy import deepcopy
from typing import Any, Dict, List, Optional, Sequence, Tuple, Union

from .memory_base import MemoryBase, MemoryUnit
from .utils import *


class DynamicMemoryUnit(MemoryUnit):
    def __init__(
        self, content: Optional[Dict] = None, required_attributes: Optional[Dict] = None
    ) -> None:
        super().__init__(content=content, required_attributes=required_attributes)


class DynamicMemory(MemoryBase):

    def __init__(
        self,
        required_attributes: Dict[Any, Any],
    ) -> None:
        super().__init__()
        self._required_attributes = deepcopy(required_attributes)
        self.add(msg=DynamicMemoryUnit(self._required_attributes))

    def add(self, msg: Union[DynamicMemoryUnit, Sequence[DynamicMemoryUnit]]) -> None:
        _memories = self._memories
        msg = convert_msg_to_sequence(msg, sequence_type=DynamicMemoryUnit)
        for unit in msg:
            if unit not in _memories:
                _memories[unit] = {}

    def pop(self, index: int) -> DynamicMemoryUnit:
        _memories = self._memories
        try:
            pop_unit = list(_memories.keys())[index]
            _memories.pop(pop_unit)
            return pop_unit
        except IndexError as e:
            raise ValueError(f"Index {index} not in memory!")

    def load(
        self,
        msg: Union[DynamicMemoryUnit, Sequence[DynamicMemoryUnit]],
        reset_memory: bool = False,
    ) -> None:
        if reset_memory:
            self.reset()
        self.add(msg)

    def reset(self) -> None:
        self._memories = {}

    def __getattr__(self, name: Any):
        _latest_memory = self._fetch_recent_memory()[-1]
        return _latest_memory[name]

    # interact
    def get(self, key: Any):
        return self.__getattr__(key)

    def update(self, key: Any, value: Any, store_in_history: bool = False):
        _latest_memory: MemoryUnit = self._fetch_recent_memory()[-1]
        if not store_in_history:
            # write in place
            _latest_memory.update({key: value})
        else:
            # insert new unit
            _content = {k: v for k, v in _latest_memory._content.items()}
            _content.update({key: value})
            self.add(DynamicMemoryUnit(_content, self._required_attributes))

    def update_dict(self, to_update_dict: Dict, store_in_history: bool = False):
        _latest_memory: MemoryUnit = self._fetch_recent_memory()[-1]
        if not store_in_history:
            # write in place
            _latest_memory.update(to_update_dict)
        else:
            # insert new unit
            _content = {k: v for k, v in _latest_memory._content.items()}
            _content.update(to_update_dict)
            self.add(DynamicMemoryUnit(_content, self._required_attributes))
