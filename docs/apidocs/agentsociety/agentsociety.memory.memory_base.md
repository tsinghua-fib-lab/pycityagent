# {py:mod}`agentsociety.memory.memory_base`

```{py:module} agentsociety.memory.memory_base
```

```{autodoc2-docstring} agentsociety.memory.memory_base
:allowtitles:
```

## Module Contents

### Classes

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`MemoryUnit <agentsociety.memory.memory_base.MemoryUnit>`
  - ```{autodoc2-docstring} agentsociety.memory.memory_base.MemoryUnit
    :summary:
    ```
* - {py:obj}`MemoryBase <agentsociety.memory.memory_base.MemoryBase>`
  - ```{autodoc2-docstring} agentsociety.memory.memory_base.MemoryBase
    :summary:
    ```
````

### Data

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`logger <agentsociety.memory.memory_base.logger>`
  - ```{autodoc2-docstring} agentsociety.memory.memory_base.logger
    :summary:
    ```
````

### API

````{py:data} logger
:canonical: agentsociety.memory.memory_base.logger
:value: >
   'getLogger(...)'

```{autodoc2-docstring} agentsociety.memory.memory_base.logger
```

````

`````{py:class} MemoryUnit(content: typing.Optional[dict] = None, required_attributes: typing.Optional[dict] = None, activate_timestamp: bool = False)
:canonical: agentsociety.memory.memory_base.MemoryUnit

```{autodoc2-docstring} agentsociety.memory.memory_base.MemoryUnit
```

```{rubric} Initialization
```

```{autodoc2-docstring} agentsociety.memory.memory_base.MemoryUnit.__init__
```

````{py:method} __getitem__(key: typing.Any) -> typing.Any
:canonical: agentsociety.memory.memory_base.MemoryUnit.__getitem__

```{autodoc2-docstring} agentsociety.memory.memory_base.MemoryUnit.__getitem__
```

````

````{py:method} _create_property(property_name: str, property_value: typing.Any)
:canonical: agentsociety.memory.memory_base.MemoryUnit._create_property

```{autodoc2-docstring} agentsociety.memory.memory_base.MemoryUnit._create_property
```

````

````{py:method} _set_attribute(property_name: str, property_value: typing.Any)
:canonical: agentsociety.memory.memory_base.MemoryUnit._set_attribute

```{autodoc2-docstring} agentsociety.memory.memory_base.MemoryUnit._set_attribute
```

````

````{py:method} update(content: dict) -> None
:canonical: agentsociety.memory.memory_base.MemoryUnit.update
:async:

```{autodoc2-docstring} agentsociety.memory.memory_base.MemoryUnit.update
```

````

````{py:method} clear() -> None
:canonical: agentsociety.memory.memory_base.MemoryUnit.clear
:async:

```{autodoc2-docstring} agentsociety.memory.memory_base.MemoryUnit.clear
```

````

````{py:method} dict_values() -> dict[typing.Any, typing.Any]
:canonical: agentsociety.memory.memory_base.MemoryUnit.dict_values
:async:

```{autodoc2-docstring} agentsociety.memory.memory_base.MemoryUnit.dict_values
```

````

`````

`````{py:class} MemoryBase()
:canonical: agentsociety.memory.memory_base.MemoryBase

Bases: {py:obj}`abc.ABC`

```{autodoc2-docstring} agentsociety.memory.memory_base.MemoryBase
```

```{rubric} Initialization
```

```{autodoc2-docstring} agentsociety.memory.memory_base.MemoryBase.__init__
```

````{py:method} add(msg: typing.Union[typing.Any, collections.abc.Sequence[typing.Any]]) -> None
:canonical: agentsociety.memory.memory_base.MemoryBase.add
:abstractmethod:
:async:

```{autodoc2-docstring} agentsociety.memory.memory_base.MemoryBase.add
```

````

````{py:method} pop(index: int) -> typing.Any
:canonical: agentsociety.memory.memory_base.MemoryBase.pop
:abstractmethod:
:async:

```{autodoc2-docstring} agentsociety.memory.memory_base.MemoryBase.pop
```

````

````{py:method} load(snapshots: typing.Union[typing.Any, collections.abc.Sequence[typing.Any]], reset_memory: bool = False) -> None
:canonical: agentsociety.memory.memory_base.MemoryBase.load
:abstractmethod:
:async:

```{autodoc2-docstring} agentsociety.memory.memory_base.MemoryBase.load
```

````

````{py:method} export() -> collections.abc.Sequence[typing.Any]
:canonical: agentsociety.memory.memory_base.MemoryBase.export
:abstractmethod:
:async:

```{autodoc2-docstring} agentsociety.memory.memory_base.MemoryBase.export
```

````

````{py:method} reset() -> None
:canonical: agentsociety.memory.memory_base.MemoryBase.reset
:abstractmethod:
:async:

```{autodoc2-docstring} agentsociety.memory.memory_base.MemoryBase.reset
```

````

````{py:method} _fetch_recent_memory(recent_n: typing.Optional[int] = None) -> collections.abc.Sequence[typing.Any]
:canonical: agentsociety.memory.memory_base.MemoryBase._fetch_recent_memory

```{autodoc2-docstring} agentsociety.memory.memory_base.MemoryBase._fetch_recent_memory
```

````

````{py:method} get(key: typing.Any)
:canonical: agentsociety.memory.memory_base.MemoryBase.get
:abstractmethod:
:async:

```{autodoc2-docstring} agentsociety.memory.memory_base.MemoryBase.get
```

````

````{py:method} update(key: typing.Any, value: typing.Any, store_snapshot: bool)
:canonical: agentsociety.memory.memory_base.MemoryBase.update
:abstractmethod:
:async:

```{autodoc2-docstring} agentsociety.memory.memory_base.MemoryBase.update
```

````

````{py:method} __getitem__(index: typing.Any) -> typing.Any
:canonical: agentsociety.memory.memory_base.MemoryBase.__getitem__

```{autodoc2-docstring} agentsociety.memory.memory_base.MemoryBase.__getitem__
```

````

`````
