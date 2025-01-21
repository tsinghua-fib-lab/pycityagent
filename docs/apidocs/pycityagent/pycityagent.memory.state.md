# {py:mod}`pycityagent.memory.state`

```{py:module} pycityagent.memory.state
```

```{autodoc2-docstring} pycityagent.memory.state
:allowtitles:
```

## Module Contents

### Classes

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`StateMemoryUnit <pycityagent.memory.state.StateMemoryUnit>`
  - ```{autodoc2-docstring} pycityagent.memory.state.StateMemoryUnit
    :summary:
    ```
* - {py:obj}`StateMemory <pycityagent.memory.state.StateMemory>`
  -
````

### API

````{py:class} StateMemoryUnit(content: typing.Optional[dict] = None, activate_timestamp: bool = False)
:canonical: pycityagent.memory.state.StateMemoryUnit

Bases: {py:obj}`pycityagent.memory.memory_base.MemoryUnit`

```{autodoc2-docstring} pycityagent.memory.state.StateMemoryUnit
```

```{rubric} Initialization
```

```{autodoc2-docstring} pycityagent.memory.state.StateMemoryUnit.__init__
```

````

`````{py:class} StateMemory(msg: typing.Optional[typing.Union[pycityagent.memory.memory_base.MemoryUnit, collections.abc.Sequence[pycityagent.memory.memory_base.MemoryUnit], dict, collections.abc.Sequence[dict]]] = None, activate_timestamp: bool = False)
:canonical: pycityagent.memory.state.StateMemory

Bases: {py:obj}`pycityagent.memory.memory_base.MemoryBase`

````{py:method} add(msg: typing.Union[pycityagent.memory.memory_base.MemoryUnit, collections.abc.Sequence[pycityagent.memory.memory_base.MemoryUnit]]) -> None
:canonical: pycityagent.memory.state.StateMemory.add
:async:

```{autodoc2-docstring} pycityagent.memory.state.StateMemory.add
```

````

````{py:method} pop(index: int) -> pycityagent.memory.memory_base.MemoryUnit
:canonical: pycityagent.memory.state.StateMemory.pop
:async:

```{autodoc2-docstring} pycityagent.memory.state.StateMemory.pop
```

````

````{py:method} load(snapshots: typing.Union[dict, collections.abc.Sequence[dict]], reset_memory: bool = False) -> None
:canonical: pycityagent.memory.state.StateMemory.load
:async:

```{autodoc2-docstring} pycityagent.memory.state.StateMemory.load
```

````

````{py:method} export() -> collections.abc.Sequence[dict]
:canonical: pycityagent.memory.state.StateMemory.export
:async:

```{autodoc2-docstring} pycityagent.memory.state.StateMemory.export
```

````

````{py:method} reset() -> None
:canonical: pycityagent.memory.state.StateMemory.reset
:async:

```{autodoc2-docstring} pycityagent.memory.state.StateMemory.reset
```

````

````{py:method} get(key: typing.Any)
:canonical: pycityagent.memory.state.StateMemory.get
:async:

```{autodoc2-docstring} pycityagent.memory.state.StateMemory.get
```

````

````{py:method} get_top_k(key: typing.Any, metric: collections.abc.Callable[[typing.Any], typing.Any], top_k: typing.Optional[int] = None, preserve_order: bool = True) -> typing.Union[collections.abc.Sequence[typing.Any], typing.Any]
:canonical: pycityagent.memory.state.StateMemory.get_top_k
:async:

```{autodoc2-docstring} pycityagent.memory.state.StateMemory.get_top_k
```

````

````{py:method} update(key: typing.Any, value: typing.Any, store_snapshot: bool = False)
:canonical: pycityagent.memory.state.StateMemory.update
:async:

```{autodoc2-docstring} pycityagent.memory.state.StateMemory.update
```

````

````{py:method} update_dict(to_update_dict: dict, store_snapshot: bool = False)
:canonical: pycityagent.memory.state.StateMemory.update_dict
:async:

```{autodoc2-docstring} pycityagent.memory.state.StateMemory.update_dict
```

````

`````
