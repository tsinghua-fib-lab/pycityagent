"""
Agent State
"""

from copy import deepcopy
from typing import Any, Dict, List, Optional, Sequence, Tuple, Union

from .const import *
from .memory_base import MemoryBase, MemoryUnit
from .utils import convert_msg_to_sequence


class StateMemoryUnit(MemoryUnit):
    def __init__(
        self,
        content: Optional[Dict] = None,
    ) -> None:
        super().__init__(
            content=content,
            required_attributes=STATE_ATTRIBUTES,
        )


class StateMemory(MemoryBase):
    def __init__(
        self,
        msg: Optional[
            Union[MemoryUnit, Sequence[MemoryUnit], Dict, Sequence[Dict]]
        ] = None,
    ) -> None:
        super().__init__()
        if msg is None:
            msg = deepcopy(STATE_ATTRIBUTES)
        msg = convert_msg_to_sequence(msg, sequence_type=StateMemoryUnit)
        self.load(msg, reset_memory=True)

    def add(self, msg: Union[MemoryUnit, Sequence[MemoryUnit]]) -> None:
        _memories = self._memories
        msg = convert_msg_to_sequence(msg, sequence_type=StateMemoryUnit)
        for unit in msg:
            if unit not in _memories:
                _memories[unit] = {}

    def pop(self, index: int) -> MemoryUnit:
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
            self.add(StateMemoryUnit(_content))

    def update_dict(self, to_update_dict: Dict, store_in_history: bool = False):
        _latest_memory: MemoryUnit = self._fetch_recent_memory()[-1]
        if not store_in_history:
            # write in place
            _latest_memory.update(to_update_dict)
        else:
            # insert new unit
            _content = {k: v for k, v in _latest_memory._content.items()}
            _content.update(to_update_dict)
            self.add(StateMemoryUnit(_content))
