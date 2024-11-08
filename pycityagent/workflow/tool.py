import asyncio
from typing import Any, Callable, Dict, List, Optional, Union
import re
from enum import Enum
import socket

class Tool:
    """Abstract tool class for callable tools."""
    async def __call__(self, context: Dict[str, Any]) -> Any:
        raise NotImplementedError