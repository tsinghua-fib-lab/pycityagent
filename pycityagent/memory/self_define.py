"""
Self Define Data
"""

from collections.abc import Callable, Sequence
from copy import deepcopy
from typing import Any, Optional, Union, cast

from ..utils.decorators import lock_decorator
from .const import *
from .memory_base import MemoryBase, MemoryUnit
from .utils import convert_msg_to_sequence


class DynamicMemoryUnit(MemoryUnit):
    def __init__(
        self,
        content: Optional[dict] = None,
        required_attributes: Optional[dict] = None,
        activate_timestamp: bool = False,
    ) -> None:
        super().__init__(
            content=content,
            required_attributes=required_attributes,
            activate_timestamp=activate_timestamp,
        )


class DynamicMemory(MemoryBase):

    def __init__(
        self,
        required_attributes: dict[Any, Any],
        activate_timestamp: bool = False,
    ) -> None:
        super().__init__()
        self._required_attributes = deepcopy(required_attributes)
        self.activate_timestamp = activate_timestamp
        msg = DynamicMemoryUnit(
            self._required_attributes, None, self.activate_timestamp
        )
        self._memories[msg] = {}

    @lock_decorator
    async def add(
        self, msg: Union[DynamicMemoryUnit, Sequence[DynamicMemoryUnit]]
    ) -> None:
        _memories = self._memories
        msg = convert_msg_to_sequence(
            msg,
            sequence_type=DynamicMemoryUnit,
            activate_timestamp=self.activate_timestamp,
        )
        for unit in msg:
            if unit not in _memories:
                _memories[unit] = {}

    @lock_decorator
    async def pop(self, index: int) -> DynamicMemoryUnit:
        _memories = self._memories
        try:
            pop_unit = list(_memories.keys())[index]
            _memories.pop(pop_unit)

            return pop_unit
        except IndexError as e:

            raise ValueError(f"Index {index} not in memory!")

    @lock_decorator
    async def load(
        self,
        snapshots: Union[dict, Sequence[dict]],
        reset_memory: bool = False,
    ) -> None:
        if reset_memory:
            self._memories = {}
        msg = convert_msg_to_sequence(
            snapshots,
            sequence_type=DynamicMemoryUnit,
            activate_timestamp=self.activate_timestamp,
        )
        for unit in msg:
            if unit not in self._memories:
                self._memories[unit] = {}

    @lock_decorator
    async def export(
        self,
    ) -> Sequence[dict]:
        _res = []
        for m in self._memories.keys():
            m = cast(DynamicMemoryUnit, m)
            _dict_values = await m.dict_values()
            _res.append(_dict_values)

        return _res

    async def reset(self) -> None:
        self._memories = {}

    # interact
    @lock_decorator
    async def get(self, key: Any):
        _latest_memories = self._fetch_recent_memory()
        _latest_memory: DynamicMemoryUnit = _latest_memories[-1]

        return _latest_memory[key]

    @lock_decorator
    async def get_top_k(
        self,
        key: Any,
        metric: Callable[[Any], Any],
        top_k: Optional[int] = None,
        preserve_order: bool = True,
    ) -> Union[Sequence[Any], Any]:
        _latest_memories = self._fetch_recent_memory()
        _latest_memory: DynamicMemoryUnit = _latest_memories[-1]
        _top_k = await _latest_memory.top_k_values(key, metric, top_k, preserve_order)

        return _top_k

    @lock_decorator
    async def update(self, key: Any, value: Any, store_snapshot: bool = False):
        _latest_memories = self._fetch_recent_memory()
        _latest_memory: DynamicMemoryUnit = _latest_memories[-1]
        if not store_snapshot:
            # write in place
            await _latest_memory.update({key: value})

        else:
            # insert new unit
            _dict_values = await _latest_memory.dict_values()
            _content = deepcopy(
                {k: v for k, v in _dict_values.items() if k not in {TIME_STAMP_KEY}}
            )
            _content.update({key: value})
            msg = DynamicMemoryUnit(
                _content, self._required_attributes, self.activate_timestamp
            )
            for unit in [msg]:
                if unit not in self._memories:
                    self._memories[unit] = {}

    @lock_decorator
    async def update_dict(self, to_update_dict: dict, store_snapshot: bool = False):
        _latest_memories = self._fetch_recent_memory()
        _latest_memory: DynamicMemoryUnit = _latest_memories[-1]
        if not store_snapshot:
            # write in place
            await _latest_memory.update(to_update_dict)
        else:
            # insert new unit
            _dict_values = await _latest_memory.dict_values()
            _content = deepcopy(
                {k: v for k, v in _dict_values.items() if k not in {TIME_STAMP_KEY}}
            )
            _content.update(to_update_dict)
            msg = DynamicMemoryUnit(
                _content, self._required_attributes, self.activate_timestamp
            )
            for unit in [msg]:
                if unit not in self._memories:
                    self._memories[unit] = {}
