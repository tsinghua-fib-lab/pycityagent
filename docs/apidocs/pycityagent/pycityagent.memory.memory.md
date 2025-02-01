# {py:mod}`pycityagent.memory.memory`

```{py:module} pycityagent.memory.memory
```

```{autodoc2-docstring} pycityagent.memory.memory
:allowtitles:
```

## Module Contents

### Classes

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`MemoryTag <pycityagent.memory.memory.MemoryTag>`
  - ```{autodoc2-docstring} pycityagent.memory.memory.MemoryTag
    :summary:
    ```
* - {py:obj}`MemoryNode <pycityagent.memory.memory.MemoryNode>`
  - ```{autodoc2-docstring} pycityagent.memory.memory.MemoryNode
    :summary:
    ```
* - {py:obj}`StreamMemory <pycityagent.memory.memory.StreamMemory>`
  - ```{autodoc2-docstring} pycityagent.memory.memory.StreamMemory
    :summary:
    ```
* - {py:obj}`StatusMemory <pycityagent.memory.memory.StatusMemory>`
  - ```{autodoc2-docstring} pycityagent.memory.memory.StatusMemory
    :summary:
    ```
* - {py:obj}`Memory <pycityagent.memory.memory.Memory>`
  - ```{autodoc2-docstring} pycityagent.memory.memory.Memory
    :summary:
    ```
````

### Data

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`logger <pycityagent.memory.memory.logger>`
  - ```{autodoc2-docstring} pycityagent.memory.memory.logger
    :summary:
    ```
````

### API

````{py:data} logger
:canonical: pycityagent.memory.memory.logger
:value: >
   'getLogger(...)'

```{autodoc2-docstring} pycityagent.memory.memory.logger
```

````

`````{py:class} MemoryTag()
:canonical: pycityagent.memory.memory.MemoryTag

Bases: {py:obj}`str`, {py:obj}`enum.Enum`

```{autodoc2-docstring} pycityagent.memory.memory.MemoryTag
```

```{rubric} Initialization
```

```{autodoc2-docstring} pycityagent.memory.memory.MemoryTag.__init__
```

````{py:attribute} MOBILITY
:canonical: pycityagent.memory.memory.MemoryTag.MOBILITY
:value: >
   'mobility'

```{autodoc2-docstring} pycityagent.memory.memory.MemoryTag.MOBILITY
```

````

````{py:attribute} SOCIAL
:canonical: pycityagent.memory.memory.MemoryTag.SOCIAL
:value: >
   'social'

```{autodoc2-docstring} pycityagent.memory.memory.MemoryTag.SOCIAL
```

````

````{py:attribute} ECONOMY
:canonical: pycityagent.memory.memory.MemoryTag.ECONOMY
:value: >
   'economy'

```{autodoc2-docstring} pycityagent.memory.memory.MemoryTag.ECONOMY
```

````

````{py:attribute} COGNITION
:canonical: pycityagent.memory.memory.MemoryTag.COGNITION
:value: >
   'cognition'

```{autodoc2-docstring} pycityagent.memory.memory.MemoryTag.COGNITION
```

````

````{py:attribute} OTHER
:canonical: pycityagent.memory.memory.MemoryTag.OTHER
:value: >
   'other'

```{autodoc2-docstring} pycityagent.memory.memory.MemoryTag.OTHER
```

````

````{py:attribute} EVENT
:canonical: pycityagent.memory.memory.MemoryTag.EVENT
:value: >
   'event'

```{autodoc2-docstring} pycityagent.memory.memory.MemoryTag.EVENT
```

````

`````

`````{py:class} MemoryNode
:canonical: pycityagent.memory.memory.MemoryNode

```{autodoc2-docstring} pycityagent.memory.memory.MemoryNode
```

````{py:attribute} tag
:canonical: pycityagent.memory.memory.MemoryNode.tag
:type: pycityagent.memory.memory.MemoryTag
:value: >
   None

```{autodoc2-docstring} pycityagent.memory.memory.MemoryNode.tag
```

````

````{py:attribute} day
:canonical: pycityagent.memory.memory.MemoryNode.day
:type: int
:value: >
   None

```{autodoc2-docstring} pycityagent.memory.memory.MemoryNode.day
```

````

````{py:attribute} t
:canonical: pycityagent.memory.memory.MemoryNode.t
:type: int
:value: >
   None

```{autodoc2-docstring} pycityagent.memory.memory.MemoryNode.t
```

````

````{py:attribute} location
:canonical: pycityagent.memory.memory.MemoryNode.location
:type: str
:value: >
   None

```{autodoc2-docstring} pycityagent.memory.memory.MemoryNode.location
```

````

````{py:attribute} description
:canonical: pycityagent.memory.memory.MemoryNode.description
:type: str
:value: >
   None

```{autodoc2-docstring} pycityagent.memory.memory.MemoryNode.description
```

````

````{py:attribute} cognition_id
:canonical: pycityagent.memory.memory.MemoryNode.cognition_id
:type: typing.Optional[int]
:value: >
   None

```{autodoc2-docstring} pycityagent.memory.memory.MemoryNode.cognition_id
```

````

````{py:attribute} id
:canonical: pycityagent.memory.memory.MemoryNode.id
:type: typing.Optional[int]
:value: >
   None

```{autodoc2-docstring} pycityagent.memory.memory.MemoryNode.id
```

````

`````

`````{py:class} StreamMemory(max_len: int = 1000)
:canonical: pycityagent.memory.memory.StreamMemory

```{autodoc2-docstring} pycityagent.memory.memory.StreamMemory
```

```{rubric} Initialization
```

```{autodoc2-docstring} pycityagent.memory.memory.StreamMemory.__init__
```

````{py:property} faiss_query
:canonical: pycityagent.memory.memory.StreamMemory.faiss_query
:type: pycityagent.memory.faiss_query.FaissQuery

```{autodoc2-docstring} pycityagent.memory.memory.StreamMemory.faiss_query
```

````

````{py:property} status_memory
:canonical: pycityagent.memory.memory.StreamMemory.status_memory

```{autodoc2-docstring} pycityagent.memory.memory.StreamMemory.status_memory
```

````

````{py:method} set_simulator(simulator)
:canonical: pycityagent.memory.memory.StreamMemory.set_simulator

```{autodoc2-docstring} pycityagent.memory.memory.StreamMemory.set_simulator
```

````

````{py:method} set_status_memory(status_memory)
:canonical: pycityagent.memory.memory.StreamMemory.set_status_memory

```{autodoc2-docstring} pycityagent.memory.memory.StreamMemory.set_status_memory
```

````

````{py:method} set_search_components(faiss_query, embedding_model)
:canonical: pycityagent.memory.memory.StreamMemory.set_search_components

```{autodoc2-docstring} pycityagent.memory.memory.StreamMemory.set_search_components
```

````

````{py:method} set_agent_id(agent_id: int)
:canonical: pycityagent.memory.memory.StreamMemory.set_agent_id

```{autodoc2-docstring} pycityagent.memory.memory.StreamMemory.set_agent_id
```

````

````{py:method} _add_memory(tag: pycityagent.memory.memory.MemoryTag, description: str) -> int
:canonical: pycityagent.memory.memory.StreamMemory._add_memory
:async:

```{autodoc2-docstring} pycityagent.memory.memory.StreamMemory._add_memory
```

````

````{py:method} add_cognition(description: str) -> int
:canonical: pycityagent.memory.memory.StreamMemory.add_cognition
:async:

```{autodoc2-docstring} pycityagent.memory.memory.StreamMemory.add_cognition
```

````

````{py:method} add_social(description: str) -> int
:canonical: pycityagent.memory.memory.StreamMemory.add_social
:async:

```{autodoc2-docstring} pycityagent.memory.memory.StreamMemory.add_social
```

````

````{py:method} add_economy(description: str) -> int
:canonical: pycityagent.memory.memory.StreamMemory.add_economy
:async:

```{autodoc2-docstring} pycityagent.memory.memory.StreamMemory.add_economy
```

````

````{py:method} add_mobility(description: str) -> int
:canonical: pycityagent.memory.memory.StreamMemory.add_mobility
:async:

```{autodoc2-docstring} pycityagent.memory.memory.StreamMemory.add_mobility
```

````

````{py:method} add_event(description: str) -> int
:canonical: pycityagent.memory.memory.StreamMemory.add_event
:async:

```{autodoc2-docstring} pycityagent.memory.memory.StreamMemory.add_event
```

````

````{py:method} add_other(description: str) -> int
:canonical: pycityagent.memory.memory.StreamMemory.add_other
:async:

```{autodoc2-docstring} pycityagent.memory.memory.StreamMemory.add_other
```

````

````{py:method} get_related_cognition(memory_id: int) -> typing.Union[pycityagent.memory.memory.MemoryNode, None]
:canonical: pycityagent.memory.memory.StreamMemory.get_related_cognition
:async:

```{autodoc2-docstring} pycityagent.memory.memory.StreamMemory.get_related_cognition
```

````

````{py:method} format_memory(memories: list[pycityagent.memory.memory.MemoryNode]) -> str
:canonical: pycityagent.memory.memory.StreamMemory.format_memory
:async:

```{autodoc2-docstring} pycityagent.memory.memory.StreamMemory.format_memory
```

````

````{py:method} get_by_ids(memory_ids: typing.Union[int, list[int]]) -> collections.abc.Coroutine[typing.Any, typing.Any, str]
:canonical: pycityagent.memory.memory.StreamMemory.get_by_ids
:async:

```{autodoc2-docstring} pycityagent.memory.memory.StreamMemory.get_by_ids
```

````

````{py:method} search(query: str, tag: typing.Optional[pycityagent.memory.memory.MemoryTag] = None, top_k: int = 3, day_range: typing.Optional[tuple[int, int]] = None, time_range: typing.Optional[tuple[int, int]] = None) -> str
:canonical: pycityagent.memory.memory.StreamMemory.search
:async:

```{autodoc2-docstring} pycityagent.memory.memory.StreamMemory.search
```

````

````{py:method} search_today(query: str = '', tag: typing.Optional[pycityagent.memory.memory.MemoryTag] = None, top_k: int = 100) -> str
:canonical: pycityagent.memory.memory.StreamMemory.search_today
:async:

```{autodoc2-docstring} pycityagent.memory.memory.StreamMemory.search_today
```

````

````{py:method} add_cognition_to_memory(memory_id: typing.Union[int, list[int]], cognition: str) -> None
:canonical: pycityagent.memory.memory.StreamMemory.add_cognition_to_memory
:async:

```{autodoc2-docstring} pycityagent.memory.memory.StreamMemory.add_cognition_to_memory
```

````

````{py:method} get_all() -> list[dict]
:canonical: pycityagent.memory.memory.StreamMemory.get_all
:async:

```{autodoc2-docstring} pycityagent.memory.memory.StreamMemory.get_all
```

````

`````

`````{py:class} StatusMemory(profile: pycityagent.memory.profile.ProfileMemory, state: pycityagent.memory.state.StateMemory, dynamic: pycityagent.memory.self_define.DynamicMemory)
:canonical: pycityagent.memory.memory.StatusMemory

```{autodoc2-docstring} pycityagent.memory.memory.StatusMemory
```

```{rubric} Initialization
```

```{autodoc2-docstring} pycityagent.memory.memory.StatusMemory.__init__
```

````{py:property} faiss_query
:canonical: pycityagent.memory.memory.StatusMemory.faiss_query
:type: pycityagent.memory.faiss_query.FaissQuery

```{autodoc2-docstring} pycityagent.memory.memory.StatusMemory.faiss_query
```

````

````{py:method} set_simulator(simulator)
:canonical: pycityagent.memory.memory.StatusMemory.set_simulator

```{autodoc2-docstring} pycityagent.memory.memory.StatusMemory.set_simulator
```

````

````{py:method} initialize_embeddings() -> None
:canonical: pycityagent.memory.memory.StatusMemory.initialize_embeddings
:async:

```{autodoc2-docstring} pycityagent.memory.memory.StatusMemory.initialize_embeddings
```

````

````{py:method} _get_memory_type_by_key(key: str) -> str
:canonical: pycityagent.memory.memory.StatusMemory._get_memory_type_by_key

```{autodoc2-docstring} pycityagent.memory.memory.StatusMemory._get_memory_type_by_key
```

````

````{py:method} set_search_components(faiss_query, embedding_model)
:canonical: pycityagent.memory.memory.StatusMemory.set_search_components

```{autodoc2-docstring} pycityagent.memory.memory.StatusMemory.set_search_components
```

````

````{py:method} set_agent_id(agent_id: int)
:canonical: pycityagent.memory.memory.StatusMemory.set_agent_id

```{autodoc2-docstring} pycityagent.memory.memory.StatusMemory.set_agent_id
```

````

````{py:method} set_semantic_templates(templates: typing.Dict[str, str])
:canonical: pycityagent.memory.memory.StatusMemory.set_semantic_templates

```{autodoc2-docstring} pycityagent.memory.memory.StatusMemory.set_semantic_templates
```

````

````{py:method} _generate_semantic_text(key: str, value: typing.Any) -> str
:canonical: pycityagent.memory.memory.StatusMemory._generate_semantic_text

```{autodoc2-docstring} pycityagent.memory.memory.StatusMemory._generate_semantic_text
```

````

````{py:method} search(query: str, top_k: int = 3, filter: typing.Optional[dict] = None) -> str
:canonical: pycityagent.memory.memory.StatusMemory.search
:async:

```{autodoc2-docstring} pycityagent.memory.memory.StatusMemory.search
```

````

````{py:method} set_embedding_fields(embedding_fields: typing.Dict[str, bool])
:canonical: pycityagent.memory.memory.StatusMemory.set_embedding_fields

```{autodoc2-docstring} pycityagent.memory.memory.StatusMemory.set_embedding_fields
```

````

````{py:method} should_embed(key: str) -> bool
:canonical: pycityagent.memory.memory.StatusMemory.should_embed

```{autodoc2-docstring} pycityagent.memory.memory.StatusMemory.should_embed
```

````

````{py:method} get(key: typing.Any, default_value: typing.Optional[typing.Any] = None, mode: typing.Union[typing.Literal[read only], typing.Literal[read and write]] = 'read only') -> typing.Any
:canonical: pycityagent.memory.memory.StatusMemory.get
:async:

```{autodoc2-docstring} pycityagent.memory.memory.StatusMemory.get
```

````

````{py:method} update(key: typing.Any, value: typing.Any, mode: typing.Union[typing.Literal[replace], typing.Literal[merge]] = 'replace', store_snapshot: bool = False, protect_llm_read_only_fields: bool = True) -> None
:canonical: pycityagent.memory.memory.StatusMemory.update
:async:

```{autodoc2-docstring} pycityagent.memory.memory.StatusMemory.update
```

````

````{py:method} _get_memory_type(mem: typing.Any) -> str
:canonical: pycityagent.memory.memory.StatusMemory._get_memory_type

```{autodoc2-docstring} pycityagent.memory.memory.StatusMemory._get_memory_type
```

````

````{py:method} add_watcher(key: str, callback: collections.abc.Callable) -> None
:canonical: pycityagent.memory.memory.StatusMemory.add_watcher
:async:

```{autodoc2-docstring} pycityagent.memory.memory.StatusMemory.add_watcher
```

````

````{py:method} export() -> tuple[collections.abc.Sequence[dict], collections.abc.Sequence[dict], collections.abc.Sequence[dict]]
:canonical: pycityagent.memory.memory.StatusMemory.export
:async:

```{autodoc2-docstring} pycityagent.memory.memory.StatusMemory.export
```

````

````{py:method} load(snapshots: tuple[collections.abc.Sequence[dict], collections.abc.Sequence[dict], collections.abc.Sequence[dict]], reset_memory: bool = True) -> None
:canonical: pycityagent.memory.memory.StatusMemory.load
:async:

```{autodoc2-docstring} pycityagent.memory.memory.StatusMemory.load
```

````

`````

`````{py:class} Memory(config: typing.Optional[dict[typing.Any, typing.Any]] = None, profile: typing.Optional[dict[typing.Any, typing.Any]] = None, base: typing.Optional[dict[typing.Any, typing.Any]] = None, activate_timestamp: bool = False, embedding_model: typing.Optional[langchain_core.embeddings.Embeddings] = None, faiss_query: typing.Optional[pycityagent.memory.faiss_query.FaissQuery] = None)
:canonical: pycityagent.memory.memory.Memory

```{autodoc2-docstring} pycityagent.memory.memory.Memory
```

```{rubric} Initialization
```

```{autodoc2-docstring} pycityagent.memory.memory.Memory.__init__
```

````{py:method} set_search_components(faiss_query: pycityagent.memory.faiss_query.FaissQuery, embedding_model: langchain_core.embeddings.Embeddings)
:canonical: pycityagent.memory.memory.Memory.set_search_components

```{autodoc2-docstring} pycityagent.memory.memory.Memory.set_search_components
```

````

````{py:method} set_agent_id(agent_id: int)
:canonical: pycityagent.memory.memory.Memory.set_agent_id

```{autodoc2-docstring} pycityagent.memory.memory.Memory.set_agent_id
```

````

````{py:method} set_simulator(simulator)
:canonical: pycityagent.memory.memory.Memory.set_simulator

```{autodoc2-docstring} pycityagent.memory.memory.Memory.set_simulator
```

````

````{py:property} status
:canonical: pycityagent.memory.memory.Memory.status
:type: pycityagent.memory.memory.StatusMemory

```{autodoc2-docstring} pycityagent.memory.memory.Memory.status
```

````

````{py:property} stream
:canonical: pycityagent.memory.memory.Memory.stream
:type: pycityagent.memory.memory.StreamMemory

```{autodoc2-docstring} pycityagent.memory.memory.Memory.stream
```

````

````{py:property} embedding_model
:canonical: pycityagent.memory.memory.Memory.embedding_model

```{autodoc2-docstring} pycityagent.memory.memory.Memory.embedding_model
```

````

````{py:property} agent_id
:canonical: pycityagent.memory.memory.Memory.agent_id

```{autodoc2-docstring} pycityagent.memory.memory.Memory.agent_id
```

````

````{py:property} faiss_query
:canonical: pycityagent.memory.memory.Memory.faiss_query
:type: pycityagent.memory.faiss_query.FaissQuery

```{autodoc2-docstring} pycityagent.memory.memory.Memory.faiss_query
```

````

````{py:method} initialize_embeddings()
:canonical: pycityagent.memory.memory.Memory.initialize_embeddings
:async:

```{autodoc2-docstring} pycityagent.memory.memory.Memory.initialize_embeddings
```

````

`````
