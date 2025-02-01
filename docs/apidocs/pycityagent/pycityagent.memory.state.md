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
  -
* - {py:obj}`StateMemory <pycityagent.memory.state.StateMemory>`
  -
````

### API

```{py:class} StateMemoryUnit(content: typing.Optional[dict] = None, activate_timestamp: bool = False)
:canonical: pycityagent.memory.state.StateMemoryUnit

Bases: {py:obj}`pycityagent.memory.memory_base.MemoryUnit`

```

`````{py:class} StateMemory(msg: typing.Optional[typing.Union[pycityagent.memory.memory_base.MemoryUnit, collections.abc.Sequence[pycityagent.memory.memory_base.MemoryUnit], dict, collections.abc.Sequence[dict]]] = None, activate_timestamp: bool = False)
:canonical: pycityagent.memory.state.StateMemory

Bases: {py:obj}`pycityagent.memory.memory_base.MemoryBase`

````{py:method} add(msg: typing.Union[pycityagent.memory.memory_base.MemoryUnit, collections.abc.Sequence[pycityagent.memory.memory_base.MemoryUnit]]) -> None
:canonical: pycityagent.memory.state.StateMemory.add
:async:

````

````{py:method} pop(index: int) -> pycityagent.memory.memory_base.MemoryUnit
:canonical: pycityagent.memory.state.StateMemory.pop
:async:

````

````{py:method} load(snapshots: typing.Union[dict, collections.abc.Sequence[dict]], reset_memory: bool = False) -> None
:canonical: pycityagent.memory.state.StateMemory.load
:async:

````

````{py:method} export() -> collections.abc.Sequence[dict]
:canonical: pycityagent.memory.state.StateMemory.export
:async:

````

````{py:method} reset() -> None
:canonical: pycityagent.memory.state.StateMemory.reset
:async:

````

````{py:method} get(key: typing.Any)
:canonical: pycityagent.memory.state.StateMemory.get
:async:

````

````{py:method} update(key: typing.Any, value: typing.Any, store_snapshot: bool = False)
:canonical: pycityagent.memory.state.StateMemory.update
:async:

````

````{py:method} update_dict(to_update_dict: dict, store_snapshot: bool = False)
:canonical: pycityagent.memory.state.StateMemory.update_dict
:async:

```{autodoc2-docstring} pycityagent.memory.state.StateMemory.update_dict
```

````

`````
