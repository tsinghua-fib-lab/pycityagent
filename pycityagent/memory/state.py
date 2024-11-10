"""
Agent State
"""

from copy import deepcopy
from typing import Any, Callable, Dict, List, Optional, Sequence, Tuple, Union

from .const import *
from .memory_base import MemoryBase, MemoryUnit
from .utils import convert_msg_to_sequence


class StateMemoryUnit(MemoryUnit):
    def __init__(
        self,
        content: Optional[Dict] = None,
        activate_timestamp: bool = False,
    ) -> None:
        super().__init__(
            content=content,
            required_attributes=STATE_ATTRIBUTES,
            activate_timestamp=activate_timestamp,
        )


class StateMemory(MemoryBase):
    def __init__(
        self,
        msg: Optional[
            Union[MemoryUnit, Sequence[MemoryUnit], Dict, Sequence[Dict]]
        ] = None,
        activate_timestamp: bool = False,
    ) -> None:
        super().__init__()
        if msg is None:
            msg = deepcopy(STATE_ATTRIBUTES)
        self.activate_timestamp = activate_timestamp
        msg = convert_msg_to_sequence(
            msg,
            sequence_type=StateMemoryUnit,
            activate_timestamp=self.activate_timestamp,
        )
        self.add(msg)

    def add(self, msg: Union[MemoryUnit, Sequence[MemoryUnit]]) -> None:
        _memories = self._memories
        msg = convert_msg_to_sequence(
            msg,
            sequence_type=StateMemoryUnit,
            activate_timestamp=self.activate_timestamp,
        )
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
        self,
        snapshots: Union[Dict, Sequence[Dict]],
        reset_memory: bool = False,
    ) -> None:
        if reset_memory:
            self.reset()
        self.add(
            convert_msg_to_sequence(
                snapshots,
                sequence_type=StateMemoryUnit,
                activate_timestamp=self.activate_timestamp,
            )
        )

    def export(
        self,
    ) -> Sequence[Dict]:
        return [m._content for m in self._memories.keys()]

    def reset(self) -> None:
        self._memories = {}

    # interact
    def get(self, key: Any):
        _latest_memory = self._fetch_recent_memory()[-1]
        return _latest_memory[key]

    def get_top_k(
        self, key: Any, metric: Callable[[Any], Any], top_k: Optional[int] = None
    ) -> Union[Sequence[Any], Any]:
        _latest_memory = self._fetch_recent_memory()[-1]
        return _latest_memory.top_k_values(key, metric, top_k)

    def update(self, key: Any, value: Any, store_snapshot: bool = False):
        _latest_memory: MemoryUnit = self._fetch_recent_memory()[-1]
        if not store_snapshot:
            # write in place
            _latest_memory.update({key: value})
        else:
            # insert new unit
            _content = deepcopy(
                {
                    k: v
                    for k, v in _latest_memory._content.items()
                    if k not in {TIME_STAMP_KEY}
                }
            )
            _content.update({key: value})
            self.add(StateMemoryUnit(_content, self.activate_timestamp))

    def update_dict(self, to_update_dict: Dict, store_snapshot: bool = False):
        _latest_memory: MemoryUnit = self._fetch_recent_memory()[-1]
        if not store_snapshot:
            # write in place
            _latest_memory.update(to_update_dict)
        else:
            # insert new unit
            _content = deepcopy(
                {
                    k: v
                    for k, v in _latest_memory._content.items()
                    if k not in {TIME_STAMP_KEY}
                }
            )
            _content.update(to_update_dict)
            self.add(StateMemoryUnit(_content, self.activate_timestamp))
