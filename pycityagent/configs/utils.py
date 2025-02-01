from __future__ import annotations

from typing import TYPE_CHECKING, Any, Union

import yaml

if TYPE_CHECKING:
    from .exp_config import ExpConfig
    from .sim_config import SimConfig


def load_config_from_file(
    filepath: str, config_type: Union[type[SimConfig], type[ExpConfig]]
) -> Union[SimConfig, ExpConfig]:
    with open(filepath, "r") as file:
        data = yaml.safe_load(file)
    return config_type(**data)
