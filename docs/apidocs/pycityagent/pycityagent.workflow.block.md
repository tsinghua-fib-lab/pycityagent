# {py:mod}`pycityagent.workflow.block`

```{py:module} pycityagent.workflow.block
```

```{autodoc2-docstring} pycityagent.workflow.block
:allowtitles:
```

## Module Contents

### Classes

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`Block <pycityagent.workflow.block.Block>`
  - ```{autodoc2-docstring} pycityagent.workflow.block.Block
    :summary:
    ```
````

### Functions

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`log_and_check_with_memory <pycityagent.workflow.block.log_and_check_with_memory>`
  - ```{autodoc2-docstring} pycityagent.workflow.block.log_and_check_with_memory
    :summary:
    ```
* - {py:obj}`log_and_check <pycityagent.workflow.block.log_and_check>`
  - ```{autodoc2-docstring} pycityagent.workflow.block.log_and_check
    :summary:
    ```
* - {py:obj}`trigger_class <pycityagent.workflow.block.trigger_class>`
  - ```{autodoc2-docstring} pycityagent.workflow.block.trigger_class
    :summary:
    ```
````

### Data

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`TRIGGER_INTERVAL <pycityagent.workflow.block.TRIGGER_INTERVAL>`
  - ```{autodoc2-docstring} pycityagent.workflow.block.TRIGGER_INTERVAL
    :summary:
    ```
````

### API

````{py:data} TRIGGER_INTERVAL
:canonical: pycityagent.workflow.block.TRIGGER_INTERVAL
:value: >
   1

```{autodoc2-docstring} pycityagent.workflow.block.TRIGGER_INTERVAL
```

````

````{py:function} log_and_check_with_memory(condition: typing.Union[collections.abc.Callable[[pycityagent.memory.Memory], collections.abc.Coroutine[typing.Any, typing.Any, bool]], collections.abc.Callable[[], collections.abc.Coroutine[typing.Any, typing.Any, bool]], collections.abc.Callable[[pycityagent.memory.Memory], bool], collections.abc.Callable[[], bool]] = lambda: True, trigger_interval: float = TRIGGER_INTERVAL, record_function_calling: bool = False)
:canonical: pycityagent.workflow.block.log_and_check_with_memory

```{autodoc2-docstring} pycityagent.workflow.block.log_and_check_with_memory
```
````

````{py:function} log_and_check(condition: typing.Union[collections.abc.Callable[[], collections.abc.Coroutine[typing.Any, typing.Any, bool]], collections.abc.Callable[[], bool]] = lambda: True, trigger_interval: float = TRIGGER_INTERVAL, record_function_calling: bool = False)
:canonical: pycityagent.workflow.block.log_and_check

```{autodoc2-docstring} pycityagent.workflow.block.log_and_check
```
````

````{py:function} trigger_class()
:canonical: pycityagent.workflow.block.trigger_class

```{autodoc2-docstring} pycityagent.workflow.block.trigger_class
```
````

`````{py:class} Block(name: str, llm: typing.Optional[pycityagent.llm.LLM] = None, memory: typing.Optional[pycityagent.memory.Memory] = None, simulator: typing.Optional[pycityagent.environment.simulator.Simulator] = None, trigger: typing.Optional[pycityagent.workflow.trigger.EventTrigger] = None)
:canonical: pycityagent.workflow.block.Block

```{autodoc2-docstring} pycityagent.workflow.block.Block
```

```{rubric} Initialization
```

```{autodoc2-docstring} pycityagent.workflow.block.Block.__init__
```

````{py:attribute} configurable_fields
:canonical: pycityagent.workflow.block.Block.configurable_fields
:type: list[str]
:value: >
   []

```{autodoc2-docstring} pycityagent.workflow.block.Block.configurable_fields
```

````

````{py:attribute} default_values
:canonical: pycityagent.workflow.block.Block.default_values
:type: dict[str, typing.Any]
:value: >
   None

```{autodoc2-docstring} pycityagent.workflow.block.Block.default_values
```

````

````{py:attribute} fields_description
:canonical: pycityagent.workflow.block.Block.fields_description
:type: dict[str, str]
:value: >
   None

```{autodoc2-docstring} pycityagent.workflow.block.Block.fields_description
```

````

````{py:method} export_config() -> dict[str, typing.Optional[str]]
:canonical: pycityagent.workflow.block.Block.export_config

```{autodoc2-docstring} pycityagent.workflow.block.Block.export_config
```

````

````{py:method} export_class_config() -> dict[str, str]
:canonical: pycityagent.workflow.block.Block.export_class_config
:classmethod:

```{autodoc2-docstring} pycityagent.workflow.block.Block.export_class_config
```

````

````{py:method} import_config(config: dict[str, typing.Union[str, dict]]) -> pycityagent.workflow.block.Block
:canonical: pycityagent.workflow.block.Block.import_config
:classmethod:

```{autodoc2-docstring} pycityagent.workflow.block.Block.import_config
```

````

````{py:method} load_from_config(config: dict[str, list[dict]]) -> None
:canonical: pycityagent.workflow.block.Block.load_from_config

```{autodoc2-docstring} pycityagent.workflow.block.Block.load_from_config
```

````

````{py:method} forward()
:canonical: pycityagent.workflow.block.Block.forward
:abstractmethod:
:async:

```{autodoc2-docstring} pycityagent.workflow.block.Block.forward
```

````

````{py:property} llm
:canonical: pycityagent.workflow.block.Block.llm
:type: pycityagent.llm.LLM

```{autodoc2-docstring} pycityagent.workflow.block.Block.llm
```

````

````{py:property} memory
:canonical: pycityagent.workflow.block.Block.memory
:type: pycityagent.memory.Memory

```{autodoc2-docstring} pycityagent.workflow.block.Block.memory
```

````

````{py:property} simulator
:canonical: pycityagent.workflow.block.Block.simulator
:type: pycityagent.environment.simulator.Simulator

```{autodoc2-docstring} pycityagent.workflow.block.Block.simulator
```

````

````{py:method} set_llm_client(llm: pycityagent.llm.LLM)
:canonical: pycityagent.workflow.block.Block.set_llm_client

```{autodoc2-docstring} pycityagent.workflow.block.Block.set_llm_client
```

````

````{py:method} set_simulator(simulator: pycityagent.environment.simulator.Simulator)
:canonical: pycityagent.workflow.block.Block.set_simulator

```{autodoc2-docstring} pycityagent.workflow.block.Block.set_simulator
```

````

````{py:method} set_memory(memory: pycityagent.memory.Memory)
:canonical: pycityagent.workflow.block.Block.set_memory

```{autodoc2-docstring} pycityagent.workflow.block.Block.set_memory
```

````

`````
