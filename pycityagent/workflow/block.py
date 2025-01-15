from __future__ import annotations

import asyncio
import functools
import inspect
import json
from collections.abc import Awaitable, Callable, Coroutine
from typing import Any, Optional, Union

from pyparsing import Dict

from ..environment.simulator import Simulator
from ..llm import LLM
from ..memory import Memory
from ..utils.decorators import record_call_aio
from ..workflow.trigger import EventTrigger

TRIGGER_INTERVAL = 1


def log_and_check_with_memory(
    condition: Union[
        Callable[[Memory], Coroutine[Any, Any, bool]],
        Callable[[], Coroutine[Any, Any, bool]],
        Callable[[Memory], bool],
        Callable[[], bool],
    ] = lambda: True,
    trigger_interval: float = TRIGGER_INTERVAL,
    record_function_calling: bool = False,
):
    """
    A decorator that logs function calls and optionally checks a condition before executing the function.

    This decorator is specifically designed to be used with the `block` method. A 'Memory' object is required in method input.

    Args:
        condition (Callable): A condition function that must be satisfied before the decorated function is executed.
                             Can be synchronous or asynchronous.
        trigger_interval (float): The interval (in seconds) to wait between condition checks.
        record_function_calling (bool): Whether to log the function call information.
    """

    def decorator(func):
        @record_call_aio(record_function_calling)
        @functools.wraps(func)
        async def wrapper(self, *args, **kwargs):
            memory = None
            for arg in list(args) + list(kwargs.values()):
                if memory is not None:
                    break
                if isinstance(arg, Memory):
                    memory = arg
            assert isinstance(memory, Memory), "Input arguments has no `Memory` object!"
            # Wait until the condition is met
            sig = inspect.signature(condition)
            params = list(sig.parameters.values())
            if len(params) == 1 and params[0].annotation is Memory:
                if inspect.iscoroutinefunction(condition):
                    while not await condition(memory):  # type:ignore
                        await asyncio.sleep(trigger_interval)
                else:
                    while not condition(memory):  # type:ignore
                        await asyncio.sleep(trigger_interval)
            elif len(params) == 0:
                if inspect.iscoroutinefunction(condition):
                    while not await condition():  # type:ignore
                        await asyncio.sleep(trigger_interval)
                else:
                    while not condition():  # type:ignore
                        await asyncio.sleep(trigger_interval)
            else:
                raise RuntimeError(
                    f"Invalid parameter format in condition function {condition}"
                )
            result = await func(self, *args, **kwargs)
            return result

        return wrapper

    return decorator


def log_and_check(
    condition: Union[
        Callable[[], Coroutine[Any, Any, bool]],
        Callable[[], bool],
    ] = lambda: True,
    trigger_interval: float = TRIGGER_INTERVAL,
    record_function_calling: bool = False,
):
    """
    A decorator that logs function calls and optionally checks a condition before executing the function.

    This decorator is specifically designed to be used with the `block` method.

    Args:
        condition (Callable): A condition function that must be satisfied before the decorated function is executed.
                             Can be synchronous or asynchronous.
        trigger_interval (float): The interval (in seconds) to wait between condition checks.
        record_function_calling (bool): Whether to log the function call information.
    """

    def decorator(func):
        @record_call_aio(record_function_calling)
        @functools.wraps(func)
        async def wrapper(self, *args, **kwargs):
            # Wait until the condition is met
            sig = inspect.signature(condition)
            params = list(sig.parameters.values())
            if len(params) == 0:
                if inspect.iscoroutinefunction(condition):
                    while not await condition():  # type:ignore
                        await asyncio.sleep(trigger_interval)
                else:
                    while not condition():  # type:ignore
                        await asyncio.sleep(trigger_interval)
            else:
                raise RuntimeError(
                    f"Invalid parameter format in condition function {condition}"
                )
            result = await func(self, *args, **kwargs)
            return result

        return wrapper

    return decorator


def trigger_class():
    def decorator(cls):
        original_forward = cls.forward

        @functools.wraps(original_forward)
        async def wrapped_forward(self, *args, **kwargs):
            if self.trigger is not None:
                await self.trigger.wait_for_trigger()
            return await original_forward(self, *args, **kwargs)

        cls.forward = wrapped_forward
        return cls

    return decorator


# Define a Block, similar to a layer in PyTorch
class Block:
    configurable_fields: list[str] = []
    default_values: dict[str, Any] = {}
    fields_description: dict[str, str] = {}

    def __init__(
        self,
        name: str,
        llm: Optional[LLM] = None,
        memory: Optional[Memory] = None,
        simulator: Optional[Simulator] = None,
        trigger: Optional[EventTrigger] = None,
    ):
        self.name = name
        self._llm = llm
        self._memory = memory
        self._simulator = simulator
        # 如果传入trigger，将block注入到trigger中并立即初始化
        if trigger is not None:
            trigger.block = self
            trigger.initialize()  # 立即初始化trigger
        self.trigger = trigger

    def export_config(self) -> dict[str, Optional[str]]:
        return {
            field: self.default_values.get(field, "default_value")
            for field in self.configurable_fields
        }

    @classmethod
    def export_class_config(cls) -> dict[str, str]:
        return (
            {
                field: cls.default_values.get(field, "default_value")
                for field in cls.configurable_fields
            },
            {
                field: cls.fields_description.get(field, "")
                for field in cls.configurable_fields
            }
        )

    @classmethod
    def import_config(cls, config: dict[str, Union[str, dict]]) -> Block:
        instance = cls(name=config["name"])  # type: ignore
        assert isinstance(config["config"], dict)
        for field, value in config["config"].items():
            if field in cls.configurable_fields:
                setattr(instance, field, value)

        # 递归创建子Block
        for child_config in config.get("children", []):
            child_block = Block.import_config(child_config)  # type: ignore
            setattr(instance, child_block.name.lower(), child_block)

        return instance

    def load_from_config(self, config: dict[str, list[dict]]) -> None:
        """
        使用配置更新当前Block实例的参数，并递归更新子Block。
        """
        # 更新当前Block的参数
        for field in self.configurable_fields:
            if field in config["config"]:
                if config["config"][field] != "default_value":
                    setattr(self, field, config["config"][field])

        def build_or_update_block(block_data: dict) -> Block:
            block_name = block_data["name"].lower()  # type:ignore
            existing_block = getattr(self, block_name, None)

            if existing_block:
                # 递归更新子Block
                existing_block.load_from_config(block_data)
                return existing_block
            else:
                # 创建新的子Block
                block_cls = globals().get(block_data["name"])
                if block_cls is None:
                    raise KeyError(f"Block class '{block_data['name']}' not found.")
                block_instance = block_cls.import_config(block_data)
                setattr(self, block_name, block_instance)
                return block_instance

        # 递归遍历子Block配置
        for block_data in config.get("blocks", []):
            build_or_update_block(block_data)

    async def forward(self):
        """
        Each block performs a specific reasoning task.
        To be overridden by specific block implementations.
        """
        raise NotImplementedError("Subclasses should implement this method")

    @property
    def llm(
        self,
    ) -> LLM:
        if self._llm is None:
            raise RuntimeError(f"LLM access before assignment, please `set_llm` first!")
        return self._llm

    @property
    def memory(
        self,
    ) -> Memory:
        if self._memory is None:
            raise RuntimeError(
                f"Memory access before assignment, please `set_memory` first!"
            )
        return self._memory

    @property
    def simulator(
        self,
    ) -> Simulator:
        if self._simulator is None:
            raise RuntimeError(
                f"Simulator access before assignment, please `set_simulator` first!"
            )
        return self._simulator

    def set_llm_client(self, llm: LLM):
        """
        Set the llm_client of the block.
        """
        self._llm = llm

    def set_simulator(self, simulator: Simulator):
        """
        Set the simulator of the block.
        """
        self._simulator = simulator

    def set_memory(self, memory: Memory):
        """
        Set the memory of the block.
        """
        self._memory = memory
