# {py:mod}`agentsociety.memory.state`

```{py:module} agentsociety.memory.state
```

```{autodoc2-docstring} agentsociety.memory.state
:allowtitles:
```

## Module Contents

### Classes

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`StateMemoryUnit <agentsociety.memory.state.StateMemoryUnit>`
  - ```{autodoc2-docstring} agentsociety.memory.state.StateMemoryUnit
    :summary:
    ```
* - {py:obj}`StateMemory <agentsociety.memory.state.StateMemory>`
  - ```{autodoc2-docstring} agentsociety.memory.state.StateMemory
    :summary:
    ```
````

### API

````{py:class} StateMemoryUnit(content: typing.Optional[dict] = None, activate_timestamp: bool = False)
:canonical: agentsociety.memory.state.StateMemoryUnit

Bases: {py:obj}`agentsociety.memory.memory_base.MemoryUnit`

```{autodoc2-docstring} agentsociety.memory.state.StateMemoryUnit
```

```{rubric} Initialization
```

```{autodoc2-docstring} agentsociety.memory.state.StateMemoryUnit.__init__
```

````

`````{py:class} StateMemory(msg: typing.Optional[typing.Union[agentsociety.memory.memory_base.MemoryUnit, collections.abc.Sequence[agentsociety.memory.memory_base.MemoryUnit], dict, collections.abc.Sequence[dict]]] = None, activate_timestamp: bool = False)
:canonical: agentsociety.memory.state.StateMemory

Bases: {py:obj}`agentsociety.memory.memory_base.MemoryBase`

```{autodoc2-docstring} agentsociety.memory.state.StateMemory
```

```{rubric} Initialization
```

```{autodoc2-docstring} agentsociety.memory.state.StateMemory.__init__
```

````{py:method} add(msg: typing.Union[agentsociety.memory.memory_base.MemoryUnit, collections.abc.Sequence[agentsociety.memory.memory_base.MemoryUnit]]) -> None
:canonical: agentsociety.memory.state.StateMemory.add
:async:

```{autodoc2-docstring} agentsociety.memory.state.StateMemory.add
```

````

````{py:method} pop(index: int) -> agentsociety.memory.memory_base.MemoryUnit
:canonical: agentsociety.memory.state.StateMemory.pop
:async:

```{autodoc2-docstring} agentsociety.memory.state.StateMemory.pop
```

````

````{py:method} load(snapshots: typing.Union[dict, collections.abc.Sequence[dict]], reset_memory: bool = False) -> None
:canonical: agentsociety.memory.state.StateMemory.load
:async:

```{autodoc2-docstring} agentsociety.memory.state.StateMemory.load
```

````

````{py:method} export() -> collections.abc.Sequence[dict]
:canonical: agentsociety.memory.state.StateMemory.export
:async:

```{autodoc2-docstring} agentsociety.memory.state.StateMemory.export
```

````

````{py:method} reset() -> None
:canonical: agentsociety.memory.state.StateMemory.reset
:async:

```{autodoc2-docstring} agentsociety.memory.state.StateMemory.reset
```

````

````{py:method} get(key: typing.Any)
:canonical: agentsociety.memory.state.StateMemory.get
:async:

```{autodoc2-docstring} agentsociety.memory.state.StateMemory.get
```

````

````{py:method} update(key: typing.Any, value: typing.Any, store_snapshot: bool = False)
:canonical: agentsociety.memory.state.StateMemory.update
:async:

```{autodoc2-docstring} agentsociety.memory.state.StateMemory.update
```

````

````{py:method} update_dict(to_update_dict: dict, store_snapshot: bool = False)
:canonical: agentsociety.memory.state.StateMemory.update_dict
:async:

```{autodoc2-docstring} agentsociety.memory.state.StateMemory.update_dict
```

````

`````
