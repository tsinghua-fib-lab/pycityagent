from typing import Any, Dict, List, Optional, Sequence, Tuple, Union

from .memory_unit import MemoryUnit


def convert_msg_to_sequence(
    msg: Union[MemoryUnit, Sequence[MemoryUnit], Dict, Sequence[Dict]]
) -> Sequence[MemoryUnit]:
    """
    Converts the input message into a sequence of `MemoryUnit` objects.

    This function handles various input types, including a single `MemoryUnit`, a sequence of `MemoryUnit` objects,
    a dictionary, or a sequence of dictionaries, and ensures that the output is always a sequence of `MemoryUnit` objects.

    Args:
        msg (Union[MemoryUnit, Sequence[MemoryUnit], Dict, Sequence[Dict]]):
            The input message to convert. It can be a single `MemoryUnit`, a sequence of `MemoryUnit` objects,
            a dictionary, or a sequence of dictionaries.

    Returns:
        Sequence[MemoryUnit]: A sequence of `MemoryUnit` objects.
    """
    # Convert the input message to a sequence if it is not already one
    if not isinstance(msg, Sequence):
        _sequence_msg = [msg]
    else:
        _sequence_msg = msg

    # Initialize an empty list to store the converted MemoryUnit objects
    _sequence_unit: List[MemoryUnit] = []

    # Iterate over each unit in the sequence
    for unit in _sequence_msg:
        # If the unit is not already a MemoryUnit, convert it to one
        if not isinstance(unit, MemoryUnit):
            unit = MemoryUnit(unit)
        _sequence_unit.append(unit)

    return _sequence_unit 