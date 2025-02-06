from __future__ import annotations

import asyncio
import functools
import inspect
from collections.abc import Awaitable, Callable, Coroutine
from typing import Any, Optional, Union

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

    - **Args**:
        - `condition` (Callable): A condition function that must be satisfied before the decorated function is executed.
                             Can be synchronous or asynchronous.
        - `trigger_interval` (float): The interval (in seconds) to wait between condition checks.
        - `record_function_calling` (bool): Whether to log the function call information.
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

    - **Args**:
        - `condition` (Callable): A condition function that must be satisfied before the decorated function is executed.
                             Can be synchronous or asynchronous.
        - `trigger_interval` (float): The interval (in seconds) to wait between condition checks.
        - `record_function_calling` (bool): Whether to log the function call information.
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
    """
    A foundational component similar to a layer in PyTorch, used for building complex systems.

    - **Attributes**:
        - `configurable_fields` (list[str]): A list of fields that can be configured.
        - `default_values` (dict[str, Any]): Default values for configurable fields.
        - `fields_description` (dict[str, str]): Descriptions for each configurable field.
    """

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
        """
        - **Description**:
            - Initializes a new instance of the Block class with optional LLM, Memory, Simulator, and Trigger components.

        - **Args**:
            - `name` (str): The name of the block.
            - `llm` (Optional[LLM], optional): An instance of LLM. Defaults to None.
            - `memory` (Optional[Memory], optional): An instance of Memory. Defaults to None.
            - `simulator` (Optional[Simulator], optional): An instance of Simulator. Defaults to None.
            - `trigger` (Optional[EventTrigger], optional): An event trigger that may be associated with this block. Defaults to None.
        """
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
        """
        - **Description**:
            - Exports the configuration of the block as a dictionary.

        - **Returns**:
            - `Dict[str, Optional[str]]`: A dictionary containing the configuration of the block.
        """
        return {
            field: self.default_values.get(field, "default_value")
            for field in self.configurable_fields
        }

    @classmethod
    def export_class_config(cls) -> tuple[dict[str, Any], dict[str, Any]]:
        """
        - **Description**:
            - Exports the default configuration and descriptions for the configurable fields of the class.

        - **Returns**:
            - `tuple[Dict[str, Any], Dict[str, Any]]`: A tuple containing two dictionaries, one for default values and one for field descriptions.
        """
        return (
            {
                field: cls.default_values.get(field, "default_value")
                for field in cls.configurable_fields
            },
            {
                field: cls.fields_description.get(field, "")
                for field in cls.configurable_fields
            },
        )

    @classmethod
    def import_config(cls, config: dict[str, Union[str, dict]]) -> Block:
        """
        - **Description**:
            - Creates an instance of the Block from a configuration dictionary.

        - **Args**:
            - `config` (Dict[str, Union[str, dict]]): Configuration dictionary for creating the block.

        - **Returns**:
            - `Block`: An instance of the Block created from the provided configuration.
        """
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
        - **Description**:
            - Updates the current Block instance parameters using a configuration dictionary and recursively updates its children.

        - **Args**:
            - `config` (Dict[str, List[Dict]]): Configuration dictionary for updating the block.
        """
        # 更新当前Block的参数
        for field in self.configurable_fields:
            if field in config["config"]:
                if config["config"][field] != "default_value":
                    setattr(self, field, config["config"][field])

        def build_or_update_block(block_data: dict) -> Block:
            block_name = block_data["name"]  # type:ignore
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
        for block_data in config.get("children", []):
            build_or_update_block(block_data)

    async def forward(self):
        """
        - **Description**:
            - Each block performs a specific reasoning task. This method should be overridden by subclasses.

        - **Raises**:
            - `NotImplementedError`: Subclasses must implement this method.
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
