# {py:mod}`pycityagent.memory.self_define`

```{py:module} pycityagent.memory.self_define
```

```{autodoc2-docstring} pycityagent.memory.self_define
:allowtitles:
```

## Module Contents

### Classes

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`DynamicMemoryUnit <pycityagent.memory.self_define.DynamicMemoryUnit>`
  -
* - {py:obj}`DynamicMemory <pycityagent.memory.self_define.DynamicMemory>`
  -
````

### API

```{py:class} DynamicMemoryUnit(content: typing.Optional[dict] = None, required_attributes: typing.Optional[dict] = None, activate_timestamp: bool = False)
:canonical: pycityagent.memory.self_define.DynamicMemoryUnit

Bases: {py:obj}`pycityagent.memory.memory_base.MemoryUnit`

```

`````{py:class} DynamicMemory(required_attributes: dict[typing.Any, typing.Any], activate_timestamp: bool = False)
:canonical: pycityagent.memory.self_define.DynamicMemory

Bases: {py:obj}`pycityagent.memory.memory_base.MemoryBase`

````{py:method} add(msg: typing.Union[pycityagent.memory.self_define.DynamicMemoryUnit, collections.abc.Sequence[pycityagent.memory.self_define.DynamicMemoryUnit]]) -> None
:canonical: pycityagent.memory.self_define.DynamicMemory.add
:async:

````

````{py:method} pop(index: int) -> pycityagent.memory.self_define.DynamicMemoryUnit
:canonical: pycityagent.memory.self_define.DynamicMemory.pop
:async:

````

````{py:method} load(snapshots: typing.Union[dict, collections.abc.Sequence[dict]], reset_memory: bool = False) -> None
:canonical: pycityagent.memory.self_define.DynamicMemory.load
:async:

````

````{py:method} export() -> collections.abc.Sequence[dict]
:canonical: pycityagent.memory.self_define.DynamicMemory.export
:async:

````

````{py:method} reset() -> None
:canonical: pycityagent.memory.self_define.DynamicMemory.reset
:async:

````

````{py:method} get(key: typing.Any)
:canonical: pycityagent.memory.self_define.DynamicMemory.get
:async:

````

````{py:method} update(key: typing.Any, value: typing.Any, store_snapshot: bool = False)
:canonical: pycityagent.memory.self_define.DynamicMemory.update
:async:

````

````{py:method} update_dict(to_update_dict: dict, store_snapshot: bool = False)
:canonical: pycityagent.memory.self_define.DynamicMemory.update_dict
:async:

```{autodoc2-docstring} pycityagent.memory.self_define.DynamicMemory.update_dict
```

````

`````
