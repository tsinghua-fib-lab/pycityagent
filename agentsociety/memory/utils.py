from collections.abc import Sequence
from typing import Any, Union

from .memory_base import MemoryUnit


def convert_msg_to_sequence(
    msg: Union[Any, Sequence[Any]],
    sequence_type=MemoryUnit,
    activate_timestamp: bool = False,
) -> Sequence[Any]:
    # Convert the input message to a sequence if it is not already one
    if not isinstance(msg, Sequence):
        _sequence_msg = [msg]
    else:
        _sequence_msg = msg

    # Initialize an empty list to store the converted MemoryUnit objects
    _sequence_unit = []

    # Iterate over each unit in the sequence
    for unit in _sequence_msg:
        # If the unit is not already a MemoryUnit, convert it to one
        if not isinstance(unit, sequence_type):
            unit = sequence_type(content=unit, activate_timestamp=activate_timestamp)
        _sequence_unit.append(unit)

    return _sequence_unit
