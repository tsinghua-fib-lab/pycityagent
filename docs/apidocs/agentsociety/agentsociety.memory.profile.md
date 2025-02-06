# {py:mod}`agentsociety.memory.profile`

```{py:module} agentsociety.memory.profile
```

```{autodoc2-docstring} agentsociety.memory.profile
:allowtitles:
```

## Module Contents

### Classes

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`ProfileMemoryUnit <agentsociety.memory.profile.ProfileMemoryUnit>`
  - ```{autodoc2-docstring} agentsociety.memory.profile.ProfileMemoryUnit
    :summary:
    ```
* - {py:obj}`ProfileMemory <agentsociety.memory.profile.ProfileMemory>`
  - ```{autodoc2-docstring} agentsociety.memory.profile.ProfileMemory
    :summary:
    ```
````

### API

````{py:class} ProfileMemoryUnit(content: typing.Optional[dict] = None, activate_timestamp: bool = False)
:canonical: agentsociety.memory.profile.ProfileMemoryUnit

Bases: {py:obj}`agentsociety.memory.memory_base.MemoryUnit`

```{autodoc2-docstring} agentsociety.memory.profile.ProfileMemoryUnit
```

```{rubric} Initialization
```

```{autodoc2-docstring} agentsociety.memory.profile.ProfileMemoryUnit.__init__
```

````

`````{py:class} ProfileMemory(msg: typing.Optional[typing.Union[agentsociety.memory.profile.ProfileMemoryUnit, collections.abc.Sequence[agentsociety.memory.profile.ProfileMemoryUnit], dict, collections.abc.Sequence[dict]]] = None, activate_timestamp: bool = False)
:canonical: agentsociety.memory.profile.ProfileMemory

Bases: {py:obj}`agentsociety.memory.memory_base.MemoryBase`

```{autodoc2-docstring} agentsociety.memory.profile.ProfileMemory
```

```{rubric} Initialization
```

```{autodoc2-docstring} agentsociety.memory.profile.ProfileMemory.__init__
```

````{py:method} add(msg: typing.Union[agentsociety.memory.profile.ProfileMemoryUnit, collections.abc.Sequence[agentsociety.memory.profile.ProfileMemoryUnit]]) -> None
:canonical: agentsociety.memory.profile.ProfileMemory.add
:async:

```{autodoc2-docstring} agentsociety.memory.profile.ProfileMemory.add
```

````

````{py:method} pop(index: int) -> agentsociety.memory.profile.ProfileMemoryUnit
:canonical: agentsociety.memory.profile.ProfileMemory.pop
:async:

```{autodoc2-docstring} agentsociety.memory.profile.ProfileMemory.pop
```

````

````{py:method} load(snapshots: typing.Union[dict, collections.abc.Sequence[dict]], reset_memory: bool = False) -> None
:canonical: agentsociety.memory.profile.ProfileMemory.load
:async:

```{autodoc2-docstring} agentsociety.memory.profile.ProfileMemory.load
```

````

````{py:method} export() -> collections.abc.Sequence[dict]
:canonical: agentsociety.memory.profile.ProfileMemory.export
:async:

```{autodoc2-docstring} agentsociety.memory.profile.ProfileMemory.export
```

````

````{py:method} reset() -> None
:canonical: agentsociety.memory.profile.ProfileMemory.reset
:async:

```{autodoc2-docstring} agentsociety.memory.profile.ProfileMemory.reset
```

````

````{py:method} get(key: typing.Any)
:canonical: agentsociety.memory.profile.ProfileMemory.get
:async:

```{autodoc2-docstring} agentsociety.memory.profile.ProfileMemory.get
```

````

````{py:method} update(key: typing.Any, value: typing.Any, store_snapshot: bool = False)
:canonical: agentsociety.memory.profile.ProfileMemory.update
:async:

```{autodoc2-docstring} agentsociety.memory.profile.ProfileMemory.update
```

````

````{py:method} update_dict(to_update_dict: dict, store_snapshot: bool = False)
:canonical: agentsociety.memory.profile.ProfileMemory.update_dict
:async:

```{autodoc2-docstring} agentsociety.memory.profile.ProfileMemory.update_dict
```

````

`````
