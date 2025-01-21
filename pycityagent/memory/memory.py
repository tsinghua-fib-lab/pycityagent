import asyncio
import logging
from collections import defaultdict
from collections.abc import Callable, Coroutine, Sequence
from copy import deepcopy
from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, Literal, Optional, Union

from langchain_core.embeddings import Embeddings
from pyparsing import deque

from ..utils.decorators import lock_decorator
from .const import *
from .faiss_query import FaissQuery
from .profile import ProfileMemory
from .self_define import DynamicMemory
from .state import StateMemory

logger = logging.getLogger("pycityagent")


class MemoryTag(str, Enum):
    """记忆标签枚举类"""

    MOBILITY = "mobility"
    SOCIAL = "social"
    ECONOMY = "economy"
    COGNITION = "cognition"
    OTHER = "other"
    EVENT = "event"


@dataclass
class MemoryNode:
    """记忆节点"""

    tag: MemoryTag
    day: int
    t: int
    location: str
    description: str
    cognition_id: Optional[int] = None  # 关联的认知记忆ID
    id: Optional[int] = None  # 记忆ID


class StreamMemory:
    """用于存储时序性的流式信息"""

    def __init__(self, max_len: int = 1000):
        self._memories: deque = deque(maxlen=max_len)  # 限制最大存储量
        self._memory_id_counter: int = 0  # 用于生成唯一ID
        self._faiss_query = None
        self._embedding_model = None
        self._agent_id = -1
        self._status_memory = None
        self._simulator = None

    @property
    def faiss_query(
        self,
    ) -> FaissQuery:
        assert self._faiss_query is not None
        return self._faiss_query

    @property
    def status_memory(
        self,
    ):
        assert self._status_memory is not None
        return self._status_memory

    def set_simulator(self, simulator):
        self._simulator = simulator

    def set_status_memory(self, status_memory):
        self._status_memory = status_memory

    def set_search_components(self, faiss_query, embedding_model):
        """设置搜索所需的组件"""
        self._faiss_query = faiss_query
        self._embedding_model = embedding_model

    def set_agent_id(self, agent_id: int):
        """设置agent_id"""
        self._agent_id = agent_id

    async def _add_memory(self, tag: MemoryTag, description: str) -> int:
        """添加记忆节点的通用方法，返回记忆节点ID"""
        if self._simulator is not None:
            day = int(await self._simulator.get_simulator_day())
            t = int(await self._simulator.get_time())
        else:
            day = 1
            t = 1
        position = await self.status_memory.get("position")
        if "aoi_position" in position:
            location = position["aoi_position"]["aoi_id"]
        elif "lane_position" in position:
            location = position["lane_position"]["lane_id"]
        else:
            location = "unknown"

        current_id = self._memory_id_counter
        self._memory_id_counter += 1
        memory_node = MemoryNode(
            tag=tag,
            day=day,
            t=t,
            location=location,
            description=description,
            id=current_id,
        )
        self._memories.append(memory_node)

        # 为新记忆创建 embedding
        if self._embedding_model and self._faiss_query:
            await self.faiss_query.add_documents(
                agent_id=self._agent_id,
                documents=description,
                extra_tags={
                    "type": "stream",
                    "tag": tag,
                    "day": day,
                    "time": t,
                },
            )

        return current_id

    async def add_cognition(self, description: str) -> int:
        """添加认知记忆 Add cognition memory"""
        return await self._add_memory(MemoryTag.COGNITION, description)

    async def add_social(self, description: str) -> int:
        """添加社交记忆 Add social memory"""
        return await self._add_memory(MemoryTag.SOCIAL, description)

    async def add_economy(self, description: str) -> int:
        """添加经济记忆 Add economy memory"""
        return await self._add_memory(MemoryTag.ECONOMY, description)

    async def add_mobility(self, description: str) -> int:
        """添加移动记忆 Add mobility memory"""
        return await self._add_memory(MemoryTag.MOBILITY, description)

    async def add_event(self, description: str) -> int:
        """添加事件记忆 Add event memory"""
        return await self._add_memory(MemoryTag.EVENT, description)

    async def add_other(self, description: str) -> int:
        """添加其他记忆 Add other memory"""
        return await self._add_memory(MemoryTag.OTHER, description)

    async def get_related_cognition(self, memory_id: int) -> Optional[MemoryNode]:
        """获取关联的认知记忆 Get related cognition memory"""
        for memory in self._memories:
            if memory.cognition_id == memory_id:
                for cognition_memory in self._memories:
                    if (
                        cognition_memory.tag == MemoryTag.COGNITION
                        and memory.cognition_id is not None
                    ):
                        return cognition_memory
        return None

    async def format_memory(self, memories: list[MemoryNode]) -> str:
        """格式化记忆"""
        formatted_results = []
        for memory in memories:
            memory_tag = memory.tag
            memory_day = memory.day
            memory_time_seconds = memory.t
            cognition_id = memory.cognition_id

            # 格式化时间
            if memory_time_seconds != "unknown":
                hours = memory_time_seconds // 3600
                minutes = (memory_time_seconds % 3600) // 60
                seconds = memory_time_seconds % 60
                memory_time = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
            else:
                memory_time = "unknown"

            memory_location = memory.location

            # 添加认知信息（如果存在）
            cognition_info = ""
            if cognition_id is not None:
                cognition_memory = await self.get_related_cognition(cognition_id)
                if cognition_memory:
                    cognition_info = (
                        f"\n  Related cognition: {cognition_memory.description}"
                    )

            formatted_results.append(
                f"- [{memory_tag}]: {memory.description} [day: {memory_day}, time: {memory_time}, "
                f"location: {memory_location}]{cognition_info}"
            )
        return "\n".join(formatted_results)

    async def get_by_ids(
        self, memory_ids: Union[int, list[int]]
    ) -> Coroutine[Any, Any, str]:
        """获取指定ID的记忆"""
        memories = [memory for memory in self._memories if memory.id in memory_ids]
        sorted_results = sorted(memories, key=lambda x: (x.day, x.t), reverse=True)
        return self.format_memory(sorted_results)

    async def search(
        self,
        query: str,
        tag: Optional[MemoryTag] = None,
        top_k: int = 3,
        day_range: Optional[tuple[int, int]] = None,  # 新增参数
        time_range: Optional[tuple[int, int]] = None,  # 新增参数
    ) -> str:
        """Search stream memory

        Args:
            query: Query text
            tag: Optional memory tag for filtering specific types of memories
            top_k: Number of most relevant memories to return
            day_range: Optional tuple of start and end days (start_day, end_day)
            time_range: Optional tuple of start and end times (start_time, end_time)
        """
        if not self._embedding_model or not self._faiss_query:
            return "Search components not initialized"

        filter_dict: dict[str, Any] = {"type": "stream"}

        if tag:
            filter_dict["tag"] = tag

        # 添加时间范围过滤
        if day_range:
            start_day, end_day = day_range
            filter_dict["day"] = lambda x: start_day <= x <= end_day

        if time_range:
            start_time, end_time = time_range
            filter_dict["time"] = lambda x: start_time <= x <= end_time

        top_results = await self.faiss_query.similarity_search(
            query=query,
            agent_id=self._agent_id,
            k=top_k,
            return_score_type="similarity_score",
            filter=filter_dict,
        )

        # 将结果按时间排序（先按天数，再按时间）
        sorted_results = sorted(
            top_results,
            key=lambda x: (x[2].get("day", 0), x[2].get("time", 0)),  # type:ignore
            reverse=True,
        )

        formatted_results = []
        for content, score, metadata in sorted_results:  # type:ignore
            memory_tag = metadata.get("tag", "unknown")
            memory_day = metadata.get("day", "unknown")
            memory_time_seconds = metadata.get("time", "unknown")
            cognition_id = metadata.get("cognition_id", None)

            # 格式化时间
            if memory_time_seconds != "unknown":
                hours = memory_time_seconds // 3600
                minutes = (memory_time_seconds % 3600) // 60
                seconds = memory_time_seconds % 60
                memory_time = f"{hours:02d}:{minutes:02d}:{seconds:02d}"
            else:
                memory_time = "unknown"

            memory_location = metadata.get("location", "unknown")

            # 添加认知信息（如果存在）
            cognition_info = ""
            if cognition_id is not None:
                cognition_memory = await self.get_related_cognition(cognition_id)
                if cognition_memory:
                    cognition_info = (
                        f"\n  Related cognition: {cognition_memory.description}"
                    )

            formatted_results.append(
                f"- [{memory_tag}]: {content} [day: {memory_day}, time: {memory_time}, "
                f"location: {memory_location}]{cognition_info}"
            )
        return "\n".join(formatted_results)

    async def search_today(
        self,
        query: str = "",  # 可选的查询文本
        tag: Optional[MemoryTag] = None,
        top_k: int = 100,  # 默认返回较大数量以确保获取当天所有记忆
    ) -> str:
        """Search all memory events from today

        Args:
            query: Optional query text, returns all memories of the day if empty
            tag: Optional memory tag for filtering specific types of memories
            top_k: Number of most relevant memories to return, defaults to 100

        Returns:
            str: Formatted text of today's memories
        """
        if self._simulator is None:
            return "Simulator not initialized"

        current_day = int(await self._simulator.get_simulator_day())

        # 使用 search 方法，设置 day_range 为当天
        return await self.search(
            query=query, tag=tag, top_k=top_k, day_range=(current_day, current_day)
        )

    async def add_cognition_to_memory(
        self, memory_id: Union[int, list[int]], cognition: str
    ) -> None:
        """为已存在的记忆添加认知

        Args:
            memory_id: 要添加认知的记忆ID，可以是单个ID或ID列表
            cognition: 认知描述
        """
        # 将单个ID转换为列表以统一处理
        memory_ids = [memory_id] if isinstance(memory_id, int) else memory_id

        # 找到所有对应的记忆
        target_memories = []
        for memory in self._memories:
            if memory.id in memory_ids:
                target_memories.append(memory)

        if not target_memories:
            raise ValueError(f"No memories found with ids {memory_ids}")

        # 添加认知记忆
        cognition_id = await self._add_memory(MemoryTag.COGNITION, cognition)

        # 更新所有原记忆的认知ID
        for target_memory in target_memories:
            target_memory.cognition_id = cognition_id

    async def get_all(self) -> list[MemoryNode]:
        """获取所有流式信息"""
        return list(self._memories)


class StatusMemory:
    """组合现有的三种记忆类型"""

    def __init__(
        self, profile: ProfileMemory, state: StateMemory, dynamic: DynamicMemory
    ):
        self.profile = profile
        self.state = state
        self.dynamic = dynamic
        self._faiss_query = None
        self._embedding_model = None
        self._simulator = None
        self._agent_id = -1
        self._semantic_templates = {}  # 用户可配置的模板
        self._embedding_fields = {}  # 需要 embedding 的字段
        self._embedding_field_to_doc_id = defaultdict(str)  # 新增
        self.watchers = {}  # 新增
        self._lock = asyncio.Lock()  # 新增

    @property
    def faiss_query(
        self,
    ) -> FaissQuery:
        assert self._faiss_query is not None
        return self._faiss_query

    def set_simulator(self, simulator):
        self._simulator = simulator

    async def initialize_embeddings(self) -> None:
        """初始化所有需要 embedding 的字段"""
        if not self._embedding_model or not self._faiss_query:
            logger.warning(
                "Search components not initialized, skipping embeddings initialization"
            )
            return

        # 获取所有状态信息
        profile, state, dynamic = await self.export()

        # 为每个需要 embedding 的字段创建 embedding
        for key, value in profile[0].items():
            if self.should_embed(key):
                semantic_text = self._generate_semantic_text(key, value)
                doc_ids = await self.faiss_query.add_documents(
                    agent_id=self._agent_id,
                    documents=semantic_text,
                    extra_tags={
                        "type": "profile_state",
                        "key": key,
                    },
                )
                self._embedding_field_to_doc_id[key] = doc_ids[0]

        for key, value in state[0].items():
            if self.should_embed(key):
                semantic_text = self._generate_semantic_text(key, value)
                doc_ids = await self.faiss_query.add_documents(
                    agent_id=self._agent_id,
                    documents=semantic_text,
                    extra_tags={
                        "type": "profile_state",
                        "key": key,
                    },
                )
                self._embedding_field_to_doc_id[key] = doc_ids[0]

        for key, value in dynamic[0].items():
            if self.should_embed(key):
                semantic_text = self._generate_semantic_text(key, value)
                doc_ids = await self.faiss_query.add_documents(
                    agent_id=self._agent_id,
                    documents=semantic_text,
                    extra_tags={
                        "type": "profile_state",
                        "key": key,
                    },
                )
                self._embedding_field_to_doc_id[key] = doc_ids[0]

    def _get_memory_type_by_key(self, key: str) -> str:
        """根据键名确定记忆类型"""
        try:
            if key in self.profile.__dict__:
                return "profile"
            elif key in self.state.__dict__:
                return "state"
            else:
                return "dynamic"
        except:
            return "dynamic"

    def set_search_components(self, faiss_query, embedding_model):
        """设置搜索所需的组件"""
        self._faiss_query = faiss_query
        self._embedding_model = embedding_model

    def set_agent_id(self, agent_id: int):
        """设置agent_id"""
        self._agent_id = agent_id

    def set_semantic_templates(self, templates: Dict[str, str]):
        """设置语义模板

        Args:
            templates: 键值对形式的模板字典，如 {"name": "my name is {}", "age": "I am {} years old"}
        """
        self._semantic_templates = templates

    def _generate_semantic_text(self, key: str, value: Any) -> str:
        """生成语义文本

        如果key存在于模板中，使用自定义模板
        否则使用默认模板 "my {key} is {value}"
        """
        if key in self._semantic_templates:
            return self._semantic_templates[key].format(value)
        return f"Your {key} is {value}"

    @lock_decorator
    async def search(
        self, query: str, top_k: int = 3, filter: Optional[dict] = None
    ) -> str:
        """搜索相关记忆

        Args:
            query: 查询文本
            top_k: 返回最相关的记忆数量
            filter (dict, optional): 记忆的筛选条件，如 {"key":"self_define_1",}，默认为空

        Returns:
            str: 格式化的相关记忆文本
        """
        if not self._embedding_model:
            return "Embedding model not initialized"

        filter_dict = {"type": "profile_state"}
        if filter is not None:
            filter_dict.update(filter)
        top_results: list[tuple[str, float, dict]] = (
            await self.faiss_query.similarity_search(  # type:ignore
                query=query,
                agent_id=self._agent_id,
                k=top_k,
                return_score_type="similarity_score",
                filter=filter_dict,
            )
        )
        # 格式化输出
        formatted_results = []
        for content, score, metadata in top_results:
            formatted_results.append(f"- {content} ")

        return "\n".join(formatted_results)

    def set_embedding_fields(self, embedding_fields: Dict[str, bool]):
        """设置需要 embedding 的字段"""
        self._embedding_fields = embedding_fields

    def should_embed(self, key: str) -> bool:
        """判断字段是否需要 embedding"""
        return self._embedding_fields.get(key, False)

    @lock_decorator
    async def get(
        self,
        key: Any,
        mode: Union[Literal["read only"], Literal["read and write"]] = "read only",
    ) -> Any:
        """从记忆中获取值

        Args:
            key: 要获取的键
            mode: 访问模式，"read only" 或 "read and write"

        Returns:
            获取到的值

        Raises:
            ValueError: 如果提供了无效的模式
            KeyError: 如果在任何记忆部分都找不到该键
        """
        if mode == "read only":
            process_func = deepcopy
        elif mode == "read and write":
            process_func = lambda x: x
        else:
            raise ValueError(f"Invalid get mode `{mode}`!")

        for mem in [self.state, self.profile, self.dynamic]:
            try:
                value = await mem.get(key)
                return process_func(value)
            except KeyError:
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
                logger.warning(f"Trying to write protected key `{key}`!")
                return

        for mem in [self.state, self.profile, self.dynamic]:
            try:
                original_value = await mem.get(key)
                if mode == "replace":
                    await mem.update(key, value, store_snapshot)
                    if self.should_embed(key) and self._embedding_model:
                        semantic_text = self._generate_semantic_text(key, value)

                        # 删除旧的 embedding
                        orig_doc_id = self._embedding_field_to_doc_id[key]
                        if orig_doc_id:
                            await self.faiss_query.delete_documents(
                                to_delete_ids=[orig_doc_id],
                            )

                        # 添加新的 embedding
                        doc_ids = await self.faiss_query.add_documents(
                            agent_id=self._agent_id,
                            documents=semantic_text,
                            extra_tags={
                                "type": self._get_memory_type(mem),
                                "key": key,
                            },
                        )
                        self._embedding_field_to_doc_id[key] = doc_ids[0]

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
                        logger.debug(
                            f"Type of {type(original_value)} does not support mode `merge`, using `replace` instead!"
                        )
                        await mem.update(key, value, store_snapshot)
                    if self.should_embed(key) and self._embedding_model:
                        semantic_text = self._generate_semantic_text(key, value)
                        doc_ids = await self.faiss_query.add_documents(
                            agent_id=self._agent_id,
                            documents=f"{key}: {str(original_value)}",
                            extra_tags={
                                "type": self._get_memory_type(mem),
                                "key": key,
                            },
                        )
                        self._embedding_field_to_doc_id[key] = doc_ids[0]
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
        if mem is self.state:
            return "state"
        elif mem is self.profile:
            return "profile"
        else:
            return "dynamic"

    @lock_decorator
    async def add_watcher(self, key: str, callback: Callable) -> None:
        """添加值变更的监听器"""
        if key not in self.watchers:
            self.watchers[key] = []
        self.watchers[key].append(callback)

    async def export(
        self,
    ) -> tuple[Sequence[dict], Sequence[dict], Sequence[dict]]:
        """
        Exports the current state of all memory sections.

        Returns:
            tuple[Sequence[dict], Sequence[dict], Sequence[dict]]: A tuple containing the exported data of profile, state, and dynamic memory sections.
        """
        return (
            await self.profile.export(),
            await self.state.export(),
            await self.dynamic.export(),
        )

    async def load(
        self,
        snapshots: tuple[Sequence[dict], Sequence[dict], Sequence[dict]],
        reset_memory: bool = True,
    ) -> None:
        """
        Import the snapshot memories of all sections.

        Args:
            snapshots (tuple[Sequence[dict], Sequence[dict], Sequence[dict]]): The exported snapshots.
            reset_memory (bool): Whether to reset previous memory.
        """
        _profile_snapshot, _state_snapshot, _dynamic_snapshot = snapshots
        for _snapshot, _mem in zip(
            [_profile_snapshot, _state_snapshot, _dynamic_snapshot],
            [self.state, self.profile, self.dynamic],
        ):
            if _snapshot:
                await _mem.load(snapshots=_snapshot, reset_memory=reset_memory)


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
        config: Optional[dict[Any, Any]] = None,
        profile: Optional[dict[Any, Any]] = None,
        base: Optional[dict[Any, Any]] = None,
        activate_timestamp: bool = False,
        embedding_model: Optional[Embeddings] = None,
        faiss_query: Optional[FaissQuery] = None,
    ) -> None:
        """
        Initializes the Memory with optional configuration.

        Args:
            config (Optional[dict[Any, Any]], optional):
                A configuration dictionary for dynamic memory. The dictionary format is:
                - Key: The name of the dynamic memory field.
                - Value: Can be one of two formats:
                    1. A tuple where the first element is a variable type (e.g., int, str, etc.), and the second element is the default value for this field.
                    2. A callable that returns the default value when invoked (useful for complex default values).
                Note: If a key in `config` overlaps with predefined attributes in `PROFILE_ATTRIBUTES` or `STATE_ATTRIBUTES`, a warning will be logged, and the key will be ignored.
                Defaults to None.
            profile (Optional[dict[Any, Any]], optional): profile attribute dict.
            base (Optional[dict[Any, Any]], optional): base attribute dict from City Simulator.
            motion (Optional[dict[Any, Any]], optional): motion attribute dict from City Simulator.
            activate_timestamp (bool): Whether activate timestamp storage in MemoryUnit
            embedding_model (Embeddings): The embedding model for memory search.
            faiss_query (FaissQuery): The faiss_query of the agent. Defaults to None.
        """
        self.watchers: dict[str, list[Callable]] = {}
        self._lock = asyncio.Lock()
        self._agent_id: int = -1
        self._simulator = None
        self._embedding_model = embedding_model
        self._faiss_query = faiss_query
        self._semantic_templates: dict[str, str] = {}
        _dynamic_config: dict[Any, Any] = {}
        _state_config: dict[Any, Any] = {}
        _profile_config: dict[Any, Any] = {}
        self._embedding_fields: dict[str, bool] = {}
        self._embedding_field_to_doc_id: dict[Any, str] = defaultdict(str)

        if config is not None:
            for k, v in config.items():
                try:
                    # 处理不同长度的配置元组
                    if isinstance(v, tuple):
                        if len(v) == 4:  # (_type, _value, enable_embedding, template)
                            _type, _value, enable_embedding, template = v
                            self._embedding_fields[k] = enable_embedding
                            self._semantic_templates[k] = template
                        elif len(v) == 3:  # (_type, _value, enable_embedding)
                            _type, _value, enable_embedding = v
                            self._embedding_fields[k] = enable_embedding
                        else:  # (_type, _value)
                            _type, _value = v
                            self._embedding_fields[k] = False
                    else:
                        _type = type(v)
                        _value = v
                        self._embedding_fields[k] = False

                    # 处理类型转换
                    try:
                        if isinstance(_type, type):
                            _value = _type(_value)
                        else:
                            if isinstance(_type, deque):
                                _type.extend(_value)
                                _value = deepcopy(_type)
                            else:
                                logger.warning(f"type `{_type}` is not supported!")
                    except TypeError as e:
                        logger.warning(f"Type conversion failed for key {k}: {e}")
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
                    logger.warning(f"key `{k}` already declared in memory!")
                    continue

                _dynamic_config[k] = deepcopy(_value)

        # 初始化各类记忆
        self._dynamic = DynamicMemory(
            required_attributes=_dynamic_config, activate_timestamp=activate_timestamp
        )

        if profile is not None:
            for k, v in profile.items():
                if k not in PROFILE_ATTRIBUTES:
                    logger.warning(f"key `{k}` is not a correct `profile` field!")
                    continue
                try:
                    # 处理配置元组格式
                    if isinstance(v, tuple):
                        if len(v) == 4:  # (_type, _value, enable_embedding, template)
                            _type, _value, enable_embedding, template = v
                            self._embedding_fields[k] = enable_embedding
                            self._semantic_templates[k] = template
                        elif len(v) == 3:  # (_type, _value, enable_embedding)
                            _type, _value, enable_embedding = v
                            self._embedding_fields[k] = enable_embedding
                        else:  # (_type, _value)
                            _type, _value = v
                            self._embedding_fields[k] = False

                        # 处理类型转换
                        try:
                            if isinstance(_type, type):
                                _value = _type(_value)
                            else:
                                if isinstance(_type, deque):
                                    _type.extend(_value)
                                    _value = deepcopy(_type)
                                else:
                                    logger.warning(f"type `{_type}` is not supported!")
                        except TypeError as e:
                            logger.warning(f"Type conversion failed for key {k}: {e}")
                    else:
                        # 保持对简单键值对的兼容
                        _value = v
                        self._embedding_fields[k] = False
                except TypeError as e:
                    if isinstance(v, type):
                        _value = v()
                    else:
                        _value = v
                    self._embedding_fields[k] = False

                _profile_config[k] = deepcopy(_value)
        self._profile = ProfileMemory(
            msg=_profile_config, activate_timestamp=activate_timestamp
        )
        if base is not None:
            for k, v in base.items():
                if k not in STATE_ATTRIBUTES:
                    logger.warning(f"key `{k}` is not a correct `base` field!")
                    continue
                _state_config[k] = v

        self._state = StateMemory(
            msg=_state_config, activate_timestamp=activate_timestamp
        )

        # 组合 StatusMemory，并传递 embedding_fields 信息
        self._status = StatusMemory(
            profile=self._profile, state=self._state, dynamic=self._dynamic
        )
        self._status.set_embedding_fields(self._embedding_fields)
        self._status.set_search_components(self._faiss_query, self._embedding_model)

        # 新增 StreamMemory
        self._stream = StreamMemory()
        self._stream.set_status_memory(self._status)
        self._stream.set_search_components(self._faiss_query, self._embedding_model)

    def set_search_components(
        self,
        faiss_query: FaissQuery,
        embedding_model: Embeddings,
    ):
        self._embedding_model = embedding_model
        self._faiss_query = faiss_query
        self._stream.set_search_components(faiss_query, embedding_model)
        self._status.set_search_components(faiss_query, embedding_model)

    def set_agent_id(self, agent_id: int):
        """
        Set the FaissQuery of the agent.
        """
        self._agent_id = agent_id
        self._stream.set_agent_id(agent_id)
        self._status.set_agent_id(agent_id)

    def set_simulator(self, simulator):
        self._simulator = simulator
        self._stream.set_simulator(simulator)
        self._status.set_simulator(simulator)

    @property
    def status(self) -> StatusMemory:
        return self._status

    @property
    def stream(self) -> StreamMemory:
        return self._stream

    @property
    def embedding_model(
        self,
    ):
        if self._embedding_model is None:
            raise RuntimeError(
                f"embedding_model before assignment, please `set_embedding_model` first!"
            )
        return self._embedding_model

    @property
    def agent_id(
        self,
    ):
        if self._agent_id < 0:
            raise RuntimeError(
                f"agent_id before assignment, please `set_agent_id` first!"
            )
        return self._agent_id

    @property
    def faiss_query(self) -> FaissQuery:
        """FaissQuery"""
        if self._faiss_query is None:
            raise RuntimeError(
                f"FaissQuery access before assignment, please `set_faiss_query` first!"
            )
        return self._faiss_query

    async def initialize_embeddings(self):
        """初始化embedding"""
        await self._status.initialize_embeddings()
