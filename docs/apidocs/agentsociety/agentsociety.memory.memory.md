# {py:mod}`agentsociety.memory.memory`

```{py:module} agentsociety.memory.memory
```

```{autodoc2-docstring} agentsociety.memory.memory
:allowtitles:
```

## Module Contents

### Classes

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`MemoryTag <agentsociety.memory.memory.MemoryTag>`
  - ```{autodoc2-docstring} agentsociety.memory.memory.MemoryTag
    :summary:
    ```
* - {py:obj}`MemoryNode <agentsociety.memory.memory.MemoryNode>`
  - ```{autodoc2-docstring} agentsociety.memory.memory.MemoryNode
    :summary:
    ```
* - {py:obj}`StreamMemory <agentsociety.memory.memory.StreamMemory>`
  - ```{autodoc2-docstring} agentsociety.memory.memory.StreamMemory
    :summary:
    ```
* - {py:obj}`StatusMemory <agentsociety.memory.memory.StatusMemory>`
  - ```{autodoc2-docstring} agentsociety.memory.memory.StatusMemory
    :summary:
    ```
* - {py:obj}`Memory <agentsociety.memory.memory.Memory>`
  - ```{autodoc2-docstring} agentsociety.memory.memory.Memory
    :summary:
    ```
````

### Data

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`logger <agentsociety.memory.memory.logger>`
  - ```{autodoc2-docstring} agentsociety.memory.memory.logger
    :summary:
    ```
````

### API

````{py:data} logger
:canonical: agentsociety.memory.memory.logger
:value: >
   'getLogger(...)'

```{autodoc2-docstring} agentsociety.memory.memory.logger
```

````

`````{py:class} MemoryTag()
:canonical: agentsociety.memory.memory.MemoryTag

Bases: {py:obj}`str`, {py:obj}`enum.Enum`

```{autodoc2-docstring} agentsociety.memory.memory.MemoryTag
```

```{rubric} Initialization
```

```{autodoc2-docstring} agentsociety.memory.memory.MemoryTag.__init__
```

````{py:attribute} MOBILITY
:canonical: agentsociety.memory.memory.MemoryTag.MOBILITY
:value: >
   'mobility'

```{autodoc2-docstring} agentsociety.memory.memory.MemoryTag.MOBILITY
```

````

````{py:attribute} SOCIAL
:canonical: agentsociety.memory.memory.MemoryTag.SOCIAL
:value: >
   'social'

```{autodoc2-docstring} agentsociety.memory.memory.MemoryTag.SOCIAL
```

````

````{py:attribute} ECONOMY
:canonical: agentsociety.memory.memory.MemoryTag.ECONOMY
:value: >
   'economy'

```{autodoc2-docstring} agentsociety.memory.memory.MemoryTag.ECONOMY
```

````

````{py:attribute} COGNITION
:canonical: agentsociety.memory.memory.MemoryTag.COGNITION
:value: >
   'cognition'

```{autodoc2-docstring} agentsociety.memory.memory.MemoryTag.COGNITION
```

````

````{py:attribute} OTHER
:canonical: agentsociety.memory.memory.MemoryTag.OTHER
:value: >
   'other'

```{autodoc2-docstring} agentsociety.memory.memory.MemoryTag.OTHER
```

````

````{py:attribute} EVENT
:canonical: agentsociety.memory.memory.MemoryTag.EVENT
:value: >
   'event'

```{autodoc2-docstring} agentsociety.memory.memory.MemoryTag.EVENT
```

````

`````

`````{py:class} MemoryNode
:canonical: agentsociety.memory.memory.MemoryNode

```{autodoc2-docstring} agentsociety.memory.memory.MemoryNode
```

````{py:attribute} tag
:canonical: agentsociety.memory.memory.MemoryNode.tag
:type: agentsociety.memory.memory.MemoryTag
:value: >
   None

```{autodoc2-docstring} agentsociety.memory.memory.MemoryNode.tag
```

````

````{py:attribute} day
:canonical: agentsociety.memory.memory.MemoryNode.day
:type: int
:value: >
   None

```{autodoc2-docstring} agentsociety.memory.memory.MemoryNode.day
```

````

````{py:attribute} t
:canonical: agentsociety.memory.memory.MemoryNode.t
:type: int
:value: >
   None

```{autodoc2-docstring} agentsociety.memory.memory.MemoryNode.t
```

````

````{py:attribute} location
:canonical: agentsociety.memory.memory.MemoryNode.location
:type: str
:value: >
   None

```{autodoc2-docstring} agentsociety.memory.memory.MemoryNode.location
```

````

````{py:attribute} description
:canonical: agentsociety.memory.memory.MemoryNode.description
:type: str
:value: >
   None

```{autodoc2-docstring} agentsociety.memory.memory.MemoryNode.description
```

````

````{py:attribute} cognition_id
:canonical: agentsociety.memory.memory.MemoryNode.cognition_id
:type: typing.Optional[int]
:value: >
   None

```{autodoc2-docstring} agentsociety.memory.memory.MemoryNode.cognition_id
```

````

````{py:attribute} id
:canonical: agentsociety.memory.memory.MemoryNode.id
:type: typing.Optional[int]
:value: >
   None

```{autodoc2-docstring} agentsociety.memory.memory.MemoryNode.id
```

````

`````

`````{py:class} StreamMemory(max_len: int = 1000)
:canonical: agentsociety.memory.memory.StreamMemory

```{autodoc2-docstring} agentsociety.memory.memory.StreamMemory
```

```{rubric} Initialization
```

```{autodoc2-docstring} agentsociety.memory.memory.StreamMemory.__init__
```

````{py:property} faiss_query
:canonical: agentsociety.memory.memory.StreamMemory.faiss_query
:type: agentsociety.memory.faiss_query.FaissQuery

```{autodoc2-docstring} agentsociety.memory.memory.StreamMemory.faiss_query
```

````

````{py:property} status_memory
:canonical: agentsociety.memory.memory.StreamMemory.status_memory

```{autodoc2-docstring} agentsociety.memory.memory.StreamMemory.status_memory
```

````

````{py:method} set_simulator(simulator)
:canonical: agentsociety.memory.memory.StreamMemory.set_simulator

```{autodoc2-docstring} agentsociety.memory.memory.StreamMemory.set_simulator
```

````

````{py:method} set_status_memory(status_memory)
:canonical: agentsociety.memory.memory.StreamMemory.set_status_memory

```{autodoc2-docstring} agentsociety.memory.memory.StreamMemory.set_status_memory
```

````

````{py:method} set_search_components(faiss_query, embedding_model)
:canonical: agentsociety.memory.memory.StreamMemory.set_search_components

```{autodoc2-docstring} agentsociety.memory.memory.StreamMemory.set_search_components
```

````

````{py:method} set_agent_id(agent_id: int)
:canonical: agentsociety.memory.memory.StreamMemory.set_agent_id

```{autodoc2-docstring} agentsociety.memory.memory.StreamMemory.set_agent_id
```

````

````{py:method} _add_memory(tag: agentsociety.memory.memory.MemoryTag, description: str) -> int
:canonical: agentsociety.memory.memory.StreamMemory._add_memory
:async:

```{autodoc2-docstring} agentsociety.memory.memory.StreamMemory._add_memory
```

````

````{py:method} add_cognition(description: str) -> int
:canonical: agentsociety.memory.memory.StreamMemory.add_cognition
:async:

```{autodoc2-docstring} agentsociety.memory.memory.StreamMemory.add_cognition
```

````

````{py:method} add_social(description: str) -> int
:canonical: agentsociety.memory.memory.StreamMemory.add_social
:async:

```{autodoc2-docstring} agentsociety.memory.memory.StreamMemory.add_social
```

````

````{py:method} add_economy(description: str) -> int
:canonical: agentsociety.memory.memory.StreamMemory.add_economy
:async:

```{autodoc2-docstring} agentsociety.memory.memory.StreamMemory.add_economy
```

````

````{py:method} add_mobility(description: str) -> int
:canonical: agentsociety.memory.memory.StreamMemory.add_mobility
:async:

```{autodoc2-docstring} agentsociety.memory.memory.StreamMemory.add_mobility
```

````

````{py:method} add_event(description: str) -> int
:canonical: agentsociety.memory.memory.StreamMemory.add_event
:async:

```{autodoc2-docstring} agentsociety.memory.memory.StreamMemory.add_event
```

````

````{py:method} add_other(description: str) -> int
:canonical: agentsociety.memory.memory.StreamMemory.add_other
:async:

```{autodoc2-docstring} agentsociety.memory.memory.StreamMemory.add_other
```

````

````{py:method} get_related_cognition(memory_id: int) -> typing.Union[agentsociety.memory.memory.MemoryNode, None]
:canonical: agentsociety.memory.memory.StreamMemory.get_related_cognition
:async:

```{autodoc2-docstring} agentsociety.memory.memory.StreamMemory.get_related_cognition
```

````

````{py:method} format_memory(memories: list[agentsociety.memory.memory.MemoryNode]) -> str
:canonical: agentsociety.memory.memory.StreamMemory.format_memory
:async:

```{autodoc2-docstring} agentsociety.memory.memory.StreamMemory.format_memory
```

````

````{py:method} get_by_ids(memory_ids: typing.Union[int, list[int]]) -> str
:canonical: agentsociety.memory.memory.StreamMemory.get_by_ids
:async:

```{autodoc2-docstring} agentsociety.memory.memory.StreamMemory.get_by_ids
```

````

````{py:method} search(query: str, tag: typing.Optional[agentsociety.memory.memory.MemoryTag] = None, top_k: int = 3, day_range: typing.Optional[tuple[int, int]] = None, time_range: typing.Optional[tuple[int, int]] = None) -> str
:canonical: agentsociety.memory.memory.StreamMemory.search
:async:

```{autodoc2-docstring} agentsociety.memory.memory.StreamMemory.search
```

````

````{py:method} search_today(query: str = '', tag: typing.Optional[agentsociety.memory.memory.MemoryTag] = None, top_k: int = 100) -> str
:canonical: agentsociety.memory.memory.StreamMemory.search_today
:async:

```{autodoc2-docstring} agentsociety.memory.memory.StreamMemory.search_today
```

````

````{py:method} add_cognition_to_memory(memory_id: typing.Union[int, list[int]], cognition: str) -> None
:canonical: agentsociety.memory.memory.StreamMemory.add_cognition_to_memory
:async:

```{autodoc2-docstring} agentsociety.memory.memory.StreamMemory.add_cognition_to_memory
```

````

````{py:method} get_all() -> list[dict]
:canonical: agentsociety.memory.memory.StreamMemory.get_all
:async:

```{autodoc2-docstring} agentsociety.memory.memory.StreamMemory.get_all
```

````

`````

`````{py:class} StatusMemory(profile: agentsociety.memory.profile.ProfileMemory, state: agentsociety.memory.state.StateMemory, dynamic: agentsociety.memory.self_define.DynamicMemory)
:canonical: agentsociety.memory.memory.StatusMemory

```{autodoc2-docstring} agentsociety.memory.memory.StatusMemory
```

```{rubric} Initialization
```

```{autodoc2-docstring} agentsociety.memory.memory.StatusMemory.__init__
```

````{py:property} faiss_query
:canonical: agentsociety.memory.memory.StatusMemory.faiss_query
:type: agentsociety.memory.faiss_query.FaissQuery

```{autodoc2-docstring} agentsociety.memory.memory.StatusMemory.faiss_query
```

````

````{py:method} set_simulator(simulator)
:canonical: agentsociety.memory.memory.StatusMemory.set_simulator

```{autodoc2-docstring} agentsociety.memory.memory.StatusMemory.set_simulator
```

````

````{py:method} initialize_embeddings() -> None
:canonical: agentsociety.memory.memory.StatusMemory.initialize_embeddings
:async:

```{autodoc2-docstring} agentsociety.memory.memory.StatusMemory.initialize_embeddings
```

````

````{py:method} _get_memory_type_by_key(key: str) -> str
:canonical: agentsociety.memory.memory.StatusMemory._get_memory_type_by_key

```{autodoc2-docstring} agentsociety.memory.memory.StatusMemory._get_memory_type_by_key
```

````

````{py:method} set_search_components(faiss_query, embedding_model)
:canonical: agentsociety.memory.memory.StatusMemory.set_search_components

```{autodoc2-docstring} agentsociety.memory.memory.StatusMemory.set_search_components
```

````

````{py:method} set_agent_id(agent_id: int)
:canonical: agentsociety.memory.memory.StatusMemory.set_agent_id

```{autodoc2-docstring} agentsociety.memory.memory.StatusMemory.set_agent_id
```

````

````{py:method} set_semantic_templates(templates: typing.Dict[str, str])
:canonical: agentsociety.memory.memory.StatusMemory.set_semantic_templates

```{autodoc2-docstring} agentsociety.memory.memory.StatusMemory.set_semantic_templates
```

````

````{py:method} _generate_semantic_text(key: str, value: typing.Any) -> str
:canonical: agentsociety.memory.memory.StatusMemory._generate_semantic_text

```{autodoc2-docstring} agentsociety.memory.memory.StatusMemory._generate_semantic_text
```

````

````{py:method} search(query: str, top_k: int = 3, filter: typing.Optional[dict] = None) -> str
:canonical: agentsociety.memory.memory.StatusMemory.search
:async:

```{autodoc2-docstring} agentsociety.memory.memory.StatusMemory.search
```

````

````{py:method} set_embedding_fields(embedding_fields: typing.Dict[str, bool])
:canonical: agentsociety.memory.memory.StatusMemory.set_embedding_fields

```{autodoc2-docstring} agentsociety.memory.memory.StatusMemory.set_embedding_fields
```

````

````{py:method} should_embed(key: str) -> bool
:canonical: agentsociety.memory.memory.StatusMemory.should_embed

```{autodoc2-docstring} agentsociety.memory.memory.StatusMemory.should_embed
```

````

````{py:method} get(key: typing.Any, default_value: typing.Optional[typing.Any] = None, mode: typing.Union[typing.Literal[read only], typing.Literal[read and write]] = 'read only') -> typing.Any
:canonical: agentsociety.memory.memory.StatusMemory.get
:async:

```{autodoc2-docstring} agentsociety.memory.memory.StatusMemory.get
```

````

````{py:method} update(key: typing.Any, value: typing.Any, mode: typing.Union[typing.Literal[replace], typing.Literal[merge]] = 'replace', store_snapshot: bool = False, protect_llm_read_only_fields: bool = True) -> None
:canonical: agentsociety.memory.memory.StatusMemory.update
:async:

```{autodoc2-docstring} agentsociety.memory.memory.StatusMemory.update
```

````

````{py:method} _get_memory_type(mem: typing.Any) -> str
:canonical: agentsociety.memory.memory.StatusMemory._get_memory_type

```{autodoc2-docstring} agentsociety.memory.memory.StatusMemory._get_memory_type
```

````

````{py:method} add_watcher(key: str, callback: collections.abc.Callable) -> None
:canonical: agentsociety.memory.memory.StatusMemory.add_watcher
:async:

```{autodoc2-docstring} agentsociety.memory.memory.StatusMemory.add_watcher
```

````

````{py:method} export() -> tuple[collections.abc.Sequence[dict], collections.abc.Sequence[dict], collections.abc.Sequence[dict]]
:canonical: agentsociety.memory.memory.StatusMemory.export
:async:

```{autodoc2-docstring} agentsociety.memory.memory.StatusMemory.export
```

````

````{py:method} load(snapshots: tuple[collections.abc.Sequence[dict], collections.abc.Sequence[dict], collections.abc.Sequence[dict]], reset_memory: bool = True) -> None
:canonical: agentsociety.memory.memory.StatusMemory.load
:async:

```{autodoc2-docstring} agentsociety.memory.memory.StatusMemory.load
```

````

`````

`````{py:class} Memory(config: typing.Optional[dict[typing.Any, typing.Any]] = None, profile: typing.Optional[dict[typing.Any, typing.Any]] = None, base: typing.Optional[dict[typing.Any, typing.Any]] = None, activate_timestamp: bool = False, embedding_model: typing.Optional[langchain_core.embeddings.Embeddings] = None, faiss_query: typing.Optional[agentsociety.memory.faiss_query.FaissQuery] = None)
:canonical: agentsociety.memory.memory.Memory

```{autodoc2-docstring} agentsociety.memory.memory.Memory
```

```{rubric} Initialization
```

```{autodoc2-docstring} agentsociety.memory.memory.Memory.__init__
```

````{py:method} set_search_components(faiss_query: agentsociety.memory.faiss_query.FaissQuery, embedding_model: langchain_core.embeddings.Embeddings)
:canonical: agentsociety.memory.memory.Memory.set_search_components

```{autodoc2-docstring} agentsociety.memory.memory.Memory.set_search_components
```

````

````{py:method} set_agent_id(agent_id: int)
:canonical: agentsociety.memory.memory.Memory.set_agent_id

```{autodoc2-docstring} agentsociety.memory.memory.Memory.set_agent_id
```

````

````{py:method} set_simulator(simulator)
:canonical: agentsociety.memory.memory.Memory.set_simulator

```{autodoc2-docstring} agentsociety.memory.memory.Memory.set_simulator
```

````

````{py:property} status
:canonical: agentsociety.memory.memory.Memory.status
:type: agentsociety.memory.memory.StatusMemory

```{autodoc2-docstring} agentsociety.memory.memory.Memory.status
```

````

````{py:property} stream
:canonical: agentsociety.memory.memory.Memory.stream
:type: agentsociety.memory.memory.StreamMemory

```{autodoc2-docstring} agentsociety.memory.memory.Memory.stream
```

````

````{py:property} embedding_model
:canonical: agentsociety.memory.memory.Memory.embedding_model

```{autodoc2-docstring} agentsociety.memory.memory.Memory.embedding_model
```

````

````{py:property} agent_id
:canonical: agentsociety.memory.memory.Memory.agent_id

```{autodoc2-docstring} agentsociety.memory.memory.Memory.agent_id
```

````

````{py:property} faiss_query
:canonical: agentsociety.memory.memory.Memory.faiss_query
:type: agentsociety.memory.faiss_query.FaissQuery

```{autodoc2-docstring} agentsociety.memory.memory.Memory.faiss_query
```

````

````{py:method} initialize_embeddings()
:canonical: agentsociety.memory.memory.Memory.initialize_embeddings
:async:

```{autodoc2-docstring} agentsociety.memory.memory.Memory.initialize_embeddings
```

````

`````
