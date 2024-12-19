import asyncio
import logging
from copy import deepcopy
from datetime import datetime
from typing import Any, Callable, Dict, List, Literal, Optional, Sequence, Tuple, Union

import numpy as np
from pyparsing import deque

from ..utils.decorators import lock_decorator
from .const import *
from .profile import ProfileMemory
from .self_define import DynamicMemory
from .state import StateMemory


class Memory:
    """
    A class to manage different types of memory (state, profile, dynamic).

    Attributes:
        _state (StateMemory): Stores state-related data.
        _profile (ProfileMemory): Stores profile-related data.
        _dynamic (DynamicMemory): Stores dynamically configured data.
    """

    def __init__(
        self,
        config: Optional[Dict[Any, Any]] = None,
        profile: Optional[Dict[Any, Any]] = None,
        base: Optional[Dict[Any, Any]] = None,
        motion: Optional[Dict[Any, Any]] = None,
        activate_timestamp: bool = False,
        embedding_model: Any = None,
    ) -> None:
        """
        Initializes the Memory with optional configuration.

        Args:
            config (Optional[Dict[Any, Any]], optional):
                A configuration dictionary for dynamic memory. The dictionary format is:
                - Key: The name of the dynamic memory field.
                - Value: Can be one of two formats:
                    1. A tuple where the first element is a variable type (e.g., int, str, etc.), and the second element is the default value for this field.
                    2. A callable that returns the default value when invoked (useful for complex default values).
                Note: If a key in `config` overlaps with predefined attributes in `PROFILE_ATTRIBUTES` or `STATE_ATTRIBUTES`, a warning will be logged, and the key will be ignored.
                Defaults to None.
            profile (Optional[Dict[Any, Any]], optional): profile attribute dict.
            base (Optional[Dict[Any, Any]], optional): base attribute dict from City Simulator.
            motion (Optional[Dict[Any, Any]], optional): motion attribute dict from City Simulator.
            activate_timestamp (bool): Whether activate timestamp storage in MemoryUnit
            embedding_model (Any): The embedding model for memory search.
        """
        self.watchers: Dict[str, List[Callable]] = {}
        self._lock = asyncio.Lock()
        self.embedding_model = embedding_model

        # 初始化embedding存储
        self._embeddings = {"state": {}, "profile": {}, "dynamic": {}}

        _dynamic_config: Dict[Any, Any] = {}
        _state_config: Dict[Any, Any] = {}
        _profile_config: Dict[Any, Any] = {}
        # 记录哪些字段需要embedding
        self._embedding_fields: Dict[str, bool] = {}

        if config is not None:
            for k, v in config.items():
                try:
                    # 处理新的三元组格式
                    if isinstance(v, tuple) and len(v) == 3:
                        _type, _value, enable_embedding = v
                        self._embedding_fields[k] = enable_embedding
                    else:
                        _type, _value = v
                        self._embedding_fields[k] = False

                    try:
                        if isinstance(_type, type):
                            _value = _type(_value)
                        else:
                            if isinstance(_type, deque):
                                _type.extend(_value)
                                _value = deepcopy(_type)
                            else:
                                logging.warning(f"type `{_type}` is not supported!")
                                pass
                    except TypeError as e:
                        pass
                except TypeError as e:
                    if isinstance(v, type):
                        _value = v()
                    else:
                        _value = v
                    self._embedding_fields[k] = False

                if (
                    k in PROFILE_ATTRIBUTES
                    or k in STATE_ATTRIBUTES
                    or k == TIME_STAMP_KEY
                ):
                    logging.warning(f"key `{k}` already declared in memory!")
                    continue

                _dynamic_config[k] = deepcopy(_value)

        # 初始化各类记忆
        self._dynamic = DynamicMemory(
            required_attributes=_dynamic_config, activate_timestamp=activate_timestamp
        )

        if profile is not None:
            for k, v in profile.items():
                if k not in PROFILE_ATTRIBUTES:
                    logging.warning(f"key `{k}` is not a correct `profile` field!")
                    continue
                _profile_config[k] = v
        if motion is not None:
            for k, v in motion.items():
                if k not in STATE_ATTRIBUTES:
                    logging.warning(f"key `{k}` is not a correct `motion` field!")
                    continue
                _state_config[k] = v
        if base is not None:
            for k, v in base.items():
                if k not in STATE_ATTRIBUTES:
                    logging.warning(f"key `{k}` is not a correct `base` field!")
                    continue
                _state_config[k] = v
        self._state = StateMemory(
            msg=_state_config, activate_timestamp=activate_timestamp
        )
        self._profile = ProfileMemory(
            msg=_profile_config, activate_timestamp=activate_timestamp
        )
        self.memories = []  # 存储记忆内容
        self.embeddings = []  # 存储记忆的向量表示

    @lock_decorator
    async def get(
        self,
        key: Any,
        mode: Union[Literal["read only"], Literal["read and write"]] = "read only",
    ) -> Any:
        """
        Retrieves a value from memory based on the given key and access mode.

        Args:
            key (Any): The key of the item to retrieve.
            mode (Union[Literal["read only"], Literal["read and write"]], optional): Access mode for the item. Defaults to "read only".

        Returns:
            Any: The value associated with the key.

        Raises:
            ValueError: If an invalid mode is provided.
            KeyError: If the key is not found in any of the memory sections.
        """
        if mode == "read only":
            process_func = deepcopy
        elif mode == "read and write":
            process_func = lambda x: x
        else:
            raise ValueError(f"Invalid get mode `{mode}`!")
        for _mem in [self._state, self._profile, self._dynamic]:
            try:
                value = await _mem.get(key)
                return process_func(value)
            except KeyError as e:
                continue
        raise KeyError(f"No attribute `{key}` in memories!")

    @lock_decorator
    async def update(
        self,
        key: Any,
        value: Any,
        mode: Union[Literal["replace"], Literal["merge"]] = "replace",
        store_snapshot: bool = False,
        protect_llm_read_only_fields: bool = True,
    ) -> None:
        """更新记忆值并在必要时更新embedding"""
        if protect_llm_read_only_fields:
            if any(key in _attrs for _attrs in [STATE_ATTRIBUTES]):
                logging.warning(f"Trying to write protected key `{key}`!")
                return
        for _mem in [self._state, self._profile, self._dynamic]:
            try:
                original_value = await _mem.get(key)
                if mode == "replace":
                    await _mem.update(key, value, store_snapshot)
                    # 如果字段需要embedding，则更新embedding
                    if self.embedding_model and self._embedding_fields.get(key, False):
                        memory_type = self._get_memory_type(_mem)
                        self._embeddings[memory_type][key] = (
                            await self._generate_embedding(f"{key}: {str(value)}")
                        )
                    if key in self.watchers:
                        for callback in self.watchers[key]:
                            asyncio.create_task(callback())
                elif mode == "merge":
                    if isinstance(original_value, set):
                        original_value.update(set(value))
                    elif isinstance(original_value, dict):
                        original_value.update(dict(value))
                    elif isinstance(original_value, list):
                        original_value.extend(list(value))
                    elif isinstance(original_value, deque):
                        original_value.extend(deque(value))
                    else:
                        logging.debug(
                            f"Type of {type(original_value)} does not support mode `merge`, using `replace` instead!"
                        )
                        await _mem.update(key, value, store_snapshot)
                    if self.embedding_model and self._embedding_fields.get(key, False):
                        memory_type = self._get_memory_type(_mem)
                        self._embeddings[memory_type][key] = (
                            await self._generate_embedding(
                                f"{key}: {str(original_value)}"
                            )
                        )
                    if key in self.watchers:
                        for callback in self.watchers[key]:
                            asyncio.create_task(callback())
                else:
                    raise ValueError(f"Invalid update mode `{mode}`!")
                return
            except KeyError:
                continue
        raise KeyError(f"No attribute `{key}` in memories!")

    def _get_memory_type(self, mem: Any) -> str:
        """获取记忆类型"""
        if mem is self._state:
            return "state"
        elif mem is self._profile:
            return "profile"
        else:
            return "dynamic"

    async def _generate_embedding(self, text: str) -> np.ndarray:
        """生成文本的向量表示

        Args:
            text: 输入文本

        Returns:
            np.ndarray: 文本的向量表示

        Raises:
            ValueError: 如果embedding_model未初始化
        """
        if not self.embedding_model:
            raise RuntimeError("Embedding model not initialized")

        return await self.embedding_model.embed(text)

    async def search(self, query: str, top_k: int = 3) -> str:
        """搜索相关记忆

        Args:
            query: 查询文本
            top_k: 返回最相关的记忆数量

        Returns:
            str: 格式化的相关记忆文本
        """
        if not self.embedding_model:
            return "Embedding model not initialized"

        query_embedding = await self._generate_embedding(query)
        all_results = []

        # 搜索所有记忆类型中启用了embedding的字段
        for memory_type, embeddings in self._embeddings.items():
            for key, embedding in embeddings.items():
                similarity = self._cosine_similarity(query_embedding, embedding)
                value = await self.get(key)

                all_results.append(
                    {
                        "type": memory_type,
                        "key": key,
                        "content": f"{key}: {str(value)}",
                        "similarity": similarity,
                    }
                )

        # 按相似度排序
        all_results.sort(key=lambda x: x["similarity"], reverse=True)
        top_results = all_results[:top_k]

        # 格式化输出
        formatted_results = []
        for result in top_results:
            formatted_results.append(
                f"- [{result['type']}] {result['content']} "
                f"(相关度: {result['similarity']:.2f})"
            )

        return "\n".join(formatted_results)

    async def update_batch(
        self,
        content: Union[Dict, Sequence[Tuple[Any, Any]]],
        mode: Union[Literal["replace"], Literal["merge"]] = "replace",
        store_snapshot: bool = False,
        protect_llm_read_only_fields: bool = True,
    ) -> None:
        """
        Updates multiple values in the memory at once.

        Args:
            content (Union[Dict, Sequence[Tuple[Any, Any]]]): A dictionary or sequence of tuples containing the keys and values to update.
            mode (Union[Literal["replace"], Literal["merge"]], optional): Update mode. Defaults to "replace".
            store_snapshot (bool): Whether to store a snapshot of the memory after the update.
            protect_llm_read_only_fields (bool): Whether to protect non-self define fields from being updated.

        Raises:
            TypeError: If the content type is neither a dictionary nor a sequence of tuples.
        """
        if isinstance(content, dict):
            _list_content: List[Tuple[Any, Any]] = [(k, v) for k, v in content.items()]
        elif isinstance(content, Sequence):
            _list_content: List[Tuple[Any, Any]] = [(k, v) for k, v in content]
        else:
            raise TypeError(f"Invalid content type `{type(content)}`!")
        for k, v in _list_content[:1]:
            await self.update(k, v, mode, store_snapshot, protect_llm_read_only_fields)
        for k, v in _list_content[1:]:
            await self.update(k, v, mode, False, protect_llm_read_only_fields)

    @lock_decorator
    async def add_watcher(self, key: str, callback: Callable) -> None:
        """
        Adds a callback function to be invoked when the value
        associated with the specified key in memory is updated.

        Args:
            key (str): The key for which the watcher is being registered.
            callback (Callable): A callable function that will be executed
            whenever the value associated with the specified key is updated.

        Notes:
            If the key does not already have any watchers, it will be
            initialized with an empty list before appending the callback.
        """
        if key not in self.watchers:
            self.watchers[key] = []
        self.watchers[key].append(callback)

    @lock_decorator
    async def export(
        self,
    ) -> Tuple[Sequence[Dict], Sequence[Dict], Sequence[Dict]]:
        """
        Exports the current state of all memory sections.

        Returns:
            Tuple[Sequence[Dict], Sequence[Dict], Sequence[Dict]]: A tuple containing the exported data of profile, state, and dynamic memory sections.
        """
        return (
            await self._profile.export(),
            await self._state.export(),
            await self._dynamic.export(),
        )

    @lock_decorator
    async def load(
        self,
        snapshots: Tuple[Sequence[Dict], Sequence[Dict], Sequence[Dict]],
        reset_memory: bool = True,
    ) -> None:
        """
        Import the snapshot memories of all sections.

        Args:
            snapshots (Tuple[Sequence[Dict], Sequence[Dict], Sequence[Dict]]): The exported snapshots.
            reset_memory (bool): Whether to reset previous memory.
        """
        _profile_snapshot, _state_snapshot, _dynamic_snapshot = snapshots
        for _snapshot, _mem in zip(
            [_profile_snapshot, _state_snapshot, _dynamic_snapshot],
            [self._state, self._profile, self._dynamic],
        ):
            if _snapshot:
                await _mem.load(snapshots=_snapshot, reset_memory=reset_memory)

    @lock_decorator
    async def get_top_k(
        self,
        key: Any,
        metric: Callable[[Any], Any],
        top_k: Optional[int] = None,
        mode: Union[Literal["read only"], Literal["read and write"]] = "read only",
        preserve_order: bool = True,
    ) -> Any:
        """
        Retrieves the top-k items from the memory based on the given key and metric.

        Args:
            key (Any): The key of the item to retrieve.
            metric (Callable[[Any], Any]): A callable function that defines the metric for ranking the items.
            top_k (Optional[int], optional): The number of top items to retrieve. Defaults to None (all items).
            mode (Union[Literal["read only"], Literal["read and write"]], optional): Access mode for the item. Defaults to "read only".
            preserve_order (bool): Whether preserve original order in output values.

        Returns:
            Any: The top-k items based on the specified metric.

        Raises:
            ValueError: If an invalid mode is provided.
            KeyError: If the key is not found in any of the memory sections.
        """
        if mode == "read only":
            process_func = deepcopy
        elif mode == "read and write":
            process_func = lambda x: x
        else:
            raise ValueError(f"Invalid get mode `{mode}`!")
        for _mem in [self._state, self._profile, self._dynamic]:
            try:
                value = await _mem.get_top_k(key, metric, top_k, preserve_order)
                return process_func(value)
            except KeyError as e:
                continue
        raise KeyError(f"No attribute `{key}` in memories!")

    async def add(self, content: str, metadata: Optional[dict] = None) -> None:
        """添加新的记忆

        Args:
            content: 记忆内容
            metadata: 相关元数据，如时间、地点等
        """
        embedding = await self.embedding_model.embed(content)
        self.memories.append(
            {
                "content": content,
                "metadata": metadata or {},
                "timestamp": datetime.now(),
                "embedding": embedding,
            }
        )
        self.embeddings.append(embedding)

    def _cosine_similarity(self, v1: np.ndarray, v2: np.ndarray) -> float:
        """计算余弦相似度"""
        dot_product = np.dot(v1, v2)
        norm_v1 = np.linalg.norm(v1)
        norm_v2 = np.linalg.norm(v2)
        return dot_product / (norm_v1 * norm_v2)
