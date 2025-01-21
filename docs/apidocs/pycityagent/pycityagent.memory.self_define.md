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
  - ```{autodoc2-docstring} pycityagent.memory.self_define.DynamicMemoryUnit
    :summary:
    ```
* - {py:obj}`DynamicMemory <pycityagent.memory.self_define.DynamicMemory>`
  -
````

### API

````{py:class} DynamicMemoryUnit(content: typing.Optional[dict] = None, required_attributes: typing.Optional[dict] = None, activate_timestamp: bool = False)
:canonical: pycityagent.memory.self_define.DynamicMemoryUnit

Bases: {py:obj}`pycityagent.memory.memory_base.MemoryUnit`

```{autodoc2-docstring} pycityagent.memory.self_define.DynamicMemoryUnit
```

```{rubric} Initialization
```

```{autodoc2-docstring} pycityagent.memory.self_define.DynamicMemoryUnit.__init__
```

````

`````{py:class} DynamicMemory(required_attributes: dict[typing.Any, typing.Any], activate_timestamp: bool = False)
:canonical: pycityagent.memory.self_define.DynamicMemory

Bases: {py:obj}`pycityagent.memory.memory_base.MemoryBase`

````{py:method} add(msg: typing.Union[pycityagent.memory.self_define.DynamicMemoryUnit, collections.abc.Sequence[pycityagent.memory.self_define.DynamicMemoryUnit]]) -> None
:canonical: pycityagent.memory.self_define.DynamicMemory.add
:async:

```{autodoc2-docstring} pycityagent.memory.self_define.DynamicMemory.add
```

````

````{py:method} pop(index: int) -> pycityagent.memory.self_define.DynamicMemoryUnit
:canonical: pycityagent.memory.self_define.DynamicMemory.pop
:async:

```{autodoc2-docstring} pycityagent.memory.self_define.DynamicMemory.pop
```

````

````{py:method} load(snapshots: typing.Union[dict, collections.abc.Sequence[dict]], reset_memory: bool = False) -> None
:canonical: pycityagent.memory.self_define.DynamicMemory.load
:async:

```{autodoc2-docstring} pycityagent.memory.self_define.DynamicMemory.load
```

````

````{py:method} export() -> collections.abc.Sequence[dict]
:canonical: pycityagent.memory.self_define.DynamicMemory.export
:async:

```{autodoc2-docstring} pycityagent.memory.self_define.DynamicMemory.export
```

````

````{py:method} reset() -> None
:canonical: pycityagent.memory.self_define.DynamicMemory.reset
:async:

```{autodoc2-docstring} pycityagent.memory.self_define.DynamicMemory.reset
```

````

````{py:method} get(key: typing.Any)
:canonical: pycityagent.memory.self_define.DynamicMemory.get
:async:

```{autodoc2-docstring} pycityagent.memory.self_define.DynamicMemory.get
```

````

````{py:method} get_top_k(key: typing.Any, metric: collections.abc.Callable[[typing.Any], typing.Any], top_k: typing.Optional[int] = None, preserve_order: bool = True) -> typing.Union[collections.abc.Sequence[typing.Any], typing.Any]
:canonical: pycityagent.memory.self_define.DynamicMemory.get_top_k
:async:

```{autodoc2-docstring} pycityagent.memory.self_define.DynamicMemory.get_top_k
```

````

````{py:method} update(key: typing.Any, value: typing.Any, store_snapshot: bool = False)
:canonical: pycityagent.memory.self_define.DynamicMemory.update
:async:

```{autodoc2-docstring} pycityagent.memory.self_define.DynamicMemory.update
```

````

````{py:method} update_dict(to_update_dict: dict, store_snapshot: bool = False)
:canonical: pycityagent.memory.self_define.DynamicMemory.update_dict
:async:

```{autodoc2-docstring} pycityagent.memory.self_define.DynamicMemory.update_dict
```

````

`````
