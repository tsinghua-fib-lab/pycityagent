# {py:mod}`pycityagent.memory.profile`

```{py:module} pycityagent.memory.profile
```

```{autodoc2-docstring} pycityagent.memory.profile
:allowtitles:
```

## Module Contents

### Classes

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`ProfileMemoryUnit <pycityagent.memory.profile.ProfileMemoryUnit>`
  -
* - {py:obj}`ProfileMemory <pycityagent.memory.profile.ProfileMemory>`
  -
````

### API

```{py:class} ProfileMemoryUnit(content: typing.Optional[dict] = None, activate_timestamp: bool = False)
:canonical: pycityagent.memory.profile.ProfileMemoryUnit

Bases: {py:obj}`pycityagent.memory.memory_base.MemoryUnit`

```

`````{py:class} ProfileMemory(msg: typing.Optional[typing.Union[pycityagent.memory.profile.ProfileMemoryUnit, collections.abc.Sequence[pycityagent.memory.profile.ProfileMemoryUnit], dict, collections.abc.Sequence[dict]]] = None, activate_timestamp: bool = False)
:canonical: pycityagent.memory.profile.ProfileMemory

Bases: {py:obj}`pycityagent.memory.memory_base.MemoryBase`

````{py:method} add(msg: typing.Union[pycityagent.memory.profile.ProfileMemoryUnit, collections.abc.Sequence[pycityagent.memory.profile.ProfileMemoryUnit]]) -> None
:canonical: pycityagent.memory.profile.ProfileMemory.add
:async:

````

````{py:method} pop(index: int) -> pycityagent.memory.profile.ProfileMemoryUnit
:canonical: pycityagent.memory.profile.ProfileMemory.pop
:async:

````

````{py:method} load(snapshots: typing.Union[dict, collections.abc.Sequence[dict]], reset_memory: bool = False) -> None
:canonical: pycityagent.memory.profile.ProfileMemory.load
:async:

````

````{py:method} export() -> collections.abc.Sequence[dict]
:canonical: pycityagent.memory.profile.ProfileMemory.export
:async:

````

````{py:method} reset() -> None
:canonical: pycityagent.memory.profile.ProfileMemory.reset
:async:

````

````{py:method} get(key: typing.Any)
:canonical: pycityagent.memory.profile.ProfileMemory.get
:async:

```{autodoc2-docstring} pycityagent.memory.profile.ProfileMemory.get
```

````

````{py:method} update(key: typing.Any, value: typing.Any, store_snapshot: bool = False)
:canonical: pycityagent.memory.profile.ProfileMemory.update
:async:

````

````{py:method} update_dict(to_update_dict: dict, store_snapshot: bool = False)
:canonical: pycityagent.memory.profile.ProfileMemory.update_dict
:async:

```{autodoc2-docstring} pycityagent.memory.profile.ProfileMemory.update_dict
```

````

`````
