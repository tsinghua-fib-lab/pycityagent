import asyncio
import functools
import inspect
import time
from typing import Any, Callable, Coroutine, Optional, Union

from ..llm import LLM
from ..memory import Memory
from ..utils.decorators import record_call_aio

TRIGGER_INTERVAL = 0.1


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


# Define a Block, similar to a layer in PyTorch
class Block:
    def __init__(
        self,
        name: str,
        llm: Optional[LLM] = None,
    ):
        self.name = name
        self.llm = llm

    async def reason(self, *args, **kwargs):
        """
        Each block performs a specific reasoning task.
        To be overridden by specific block implementations.
        """
        raise NotImplementedError("Subclasses should implement this method")
