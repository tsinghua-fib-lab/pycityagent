import asyncio
import inspect
import logging
from abc import ABC, abstractmethod
from collections import defaultdict
from collections.abc import Callable, Sequence
from copy import deepcopy
from typing import Any, Optional, Union

import ray
from ray.util.queue import Queue

from ..llm import LLM, LLMConfig
from ..utils.decorators import lock_decorator

DEFAULT_ERROR_STRING = """
From `{from_uuid}` To `{to_uuid}` abort due to block `{block_name}`
"""

logger = logging.getLogger("message_interceptor")


class MessageBlockBase(ABC):
    """
    用于过滤的block
    """

    def __init__(
        self,
        name: str = "",
    ) -> None:
        self._name = name
        self._llm = None
        self._lock = asyncio.Lock()

    @property
    def llm(
        self,
    ) -> LLM:
        if self._llm is None:
            raise RuntimeError(f"LLM access before assignment, please `set_llm` first!")
        return self._llm

    @property
    def name(
        self,
    ):
        return self._name

    @property
    def has_llm(
        self,
    ) -> bool:
        return self._llm is not None

    @lock_decorator
    async def set_llm(self, llm: LLM):
        """
        Set the llm_client of the block.
        """
        self._llm = llm

    @lock_decorator
    async def set_name(self, name: str):
        """
        Set the name of the block.
        """
        self._name = name

    @lock_decorator
    async def forward(
        self,
        from_uuid: str,
        to_uuid: str,
        msg: str,
        violation_counts: dict[str, int],
        black_list: list[tuple[str, str]],
    ) -> tuple[bool, str]:
        return True, ""


@ray.remote
class MessageInterceptor:
    """
    信息拦截器
    """

    def __init__(
        self,
        blocks: Optional[list[MessageBlockBase]] = None,
        black_list: Optional[list[tuple[str, str]]] = None,
        llm_config: Optional[dict] = None,
        queue: Optional[Queue] = None,
    ) -> None:
        if blocks is not None:
            self._blocks: list[MessageBlockBase] = blocks
        else:
            self._blocks: list[MessageBlockBase] = []
        self._violation_counts: dict[str, int] = defaultdict(int)
        if black_list is not None:
            self._black_list: list[tuple[str, str]] = black_list
        else:
            self._black_list: list[tuple[str, str]] = (
                []
            )  # list[tuple(from_uuid, to_uuid)] `None` means forbidden for everyone.
        if llm_config:
            self._llm = LLM(LLMConfig(llm_config))
        else:
            self._llm = None
        self._queue = queue
        self._lock = asyncio.Lock()

    @property
    def llm(
        self,
    ) -> LLM:
        if self._llm is None:
            raise RuntimeError(f"LLM access before assignment, please `set_llm` first!")
        return self._llm

    @lock_decorator
    async def blocks(
        self,
    ) -> list[MessageBlockBase]:
        return self._blocks

    @lock_decorator
    async def set_llm(self, llm: LLM):
        """
        Set the llm_client of the block.
        """
        if self._llm is None:
            self._llm = llm

    @lock_decorator
    async def violation_counts(
        self,
    ) -> dict[str, int]:
        return deepcopy(self._violation_counts)

    @property
    def has_llm(
        self,
    ) -> bool:
        return self._llm is not None

    @lock_decorator
    async def black_list(
        self,
    ) -> list[tuple[str, str]]:
        return deepcopy(self._black_list)

    @lock_decorator
    async def add_to_black_list(
        self, black_list: Union[list[tuple[str, str]], tuple[str, str]]
    ):
        if all(isinstance(s, str) for s in black_list):
            # tuple[str,str]
            _black_list = [black_list]
        else:
            _black_list = black_list
        _black_list = [tuple(p) for p in _black_list]
        self._black_list.extend(_black_list)  # type: ignore
        self._black_list = list(set(self._black_list))

    @property
    def has_queue(
        self,
    ) -> bool:
        return self._queue is not None

    @lock_decorator
    async def set_queue(self, queue: Queue):
        """
        Set the queue of the MessageInterceptor.
        """
        self._queue = queue

    @lock_decorator
    async def remove_from_black_list(
        self, to_remove_black_list: Union[list[tuple[str, str]], tuple[str, str]]
    ):
        if all(isinstance(s, str) for s in to_remove_black_list):
            # tuple[str,str]
            _black_list = [to_remove_black_list]
        else:
            _black_list = to_remove_black_list
        _black_list_set = {tuple(p) for p in _black_list}
        self._black_list = [p for p in self._black_list if p not in _black_list_set]

    @property
    def queue(
        self,
    ) -> Queue:
        if self._queue is None:
            raise RuntimeError(
                f"Queue access before assignment, please `set_queue` first!"
            )
        return self._queue

    @lock_decorator
    async def insert_block(self, block: MessageBlockBase, index: Optional[int] = None):
        if index is None:
            index = len(self._blocks)
        self._blocks.insert(index, block)

    @lock_decorator
    async def pop_block(self, index: Optional[int] = None) -> MessageBlockBase:
        if index is None:
            index = -1
        return self._blocks.pop(index)

    @lock_decorator
    async def set_black_list(
        self, black_list: Union[list[tuple[str, str]], tuple[str, str]]
    ):
        if all(isinstance(s, str) for s in black_list):
            # tuple[str,str]
            _black_list = [black_list]
        else:
            _black_list = black_list
        _black_list = [tuple(p) for p in _black_list]
        self._black_list = list(set(_black_list))  # type: ignore

    @lock_decorator
    async def set_blocks(self, blocks: list[MessageBlockBase]):
        self._blocks = blocks

    @lock_decorator
    async def forward(
        self,
        from_uuid: str,
        to_uuid: str,
        msg: str,
    ):
        for _block in self._blocks:
            if not _block.has_llm and self.has_llm:
                await _block.set_llm(self.llm)
            func_params = inspect.signature(_block.forward).parameters
            _args = {
                "from_uuid": from_uuid,
                "to_uuid": to_uuid,
                "msg": msg,
                "violation_counts": self._violation_counts,
                "black_list": self._black_list,
            }
            _required_args = {k: v for k, v in _args.items() if k in func_params}
            res = await _block.forward(**_required_args)
            try:
                is_valid, err = res
            except TypeError as e:
                is_valid: bool = res  # type:ignore
                err = (
                    DEFAULT_ERROR_STRING.format(
                        from_uuid=from_uuid,
                        to_uuid=to_uuid,
                        block_name=f"{_block.__class__.__name__} `{_block.name}`",
                    )
                    if not is_valid
                    else ""
                )
            if not is_valid:
                if self.has_queue:
                    logger.debug(f"put `{err}` into queue")
                    await self.queue.put_async(err)  # type:ignore
                self._violation_counts[from_uuid] += 1
                print(self._black_list)
                return False
            else:
                # valid
                pass
        print(self._black_list)
        return True


class MessageBlockListenerBase(ABC):
    def __init__(
        self,
        save_queue_values: bool = False,
        get_queue_period: float = 0.1,
    ) -> None:
        self._queue = None
        self._lock = asyncio.Lock()
        self._values_from_queue: list[Any] = []
        self._save_queue_values = save_queue_values
        self._get_queue_period = get_queue_period

    @property
    def queue(
        self,
    ) -> Queue:
        if self._queue is None:
            raise RuntimeError(
                f"Queue access before assignment, please `set_queue` first!"
            )
        return self._queue

    @property
    def has_queue(
        self,
    ) -> bool:
        return self._queue is not None

    @lock_decorator
    async def set_queue(self, queue: Queue):
        """
        Set the queue of the MessageBlockListenerBase.
        """
        self._queue = queue

    @lock_decorator
    async def forward(
        self,
    ):
        while True:
            if self.has_queue:
                value = await self.queue.get_async()  # type: ignore
                if self._save_queue_values:
                    self._values_from_queue.append(value)
                logger.debug(f"get `{value}` from queue")
                # do something with the value
            await asyncio.sleep(self._get_queue_period)
