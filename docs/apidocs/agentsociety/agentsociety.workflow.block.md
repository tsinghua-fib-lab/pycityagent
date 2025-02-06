# {py:mod}`agentsociety.workflow.block`

```{py:module} agentsociety.workflow.block
```

```{autodoc2-docstring} agentsociety.workflow.block
:allowtitles:
```

## Module Contents

### Classes

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`Block <agentsociety.workflow.block.Block>`
  - ```{autodoc2-docstring} agentsociety.workflow.block.Block
    :summary:
    ```
````

### Functions

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`log_and_check_with_memory <agentsociety.workflow.block.log_and_check_with_memory>`
  - ```{autodoc2-docstring} agentsociety.workflow.block.log_and_check_with_memory
    :summary:
    ```
* - {py:obj}`log_and_check <agentsociety.workflow.block.log_and_check>`
  - ```{autodoc2-docstring} agentsociety.workflow.block.log_and_check
    :summary:
    ```
* - {py:obj}`trigger_class <agentsociety.workflow.block.trigger_class>`
  - ```{autodoc2-docstring} agentsociety.workflow.block.trigger_class
    :summary:
    ```
````

### Data

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`TRIGGER_INTERVAL <agentsociety.workflow.block.TRIGGER_INTERVAL>`
  - ```{autodoc2-docstring} agentsociety.workflow.block.TRIGGER_INTERVAL
    :summary:
    ```
````

### API

````{py:data} TRIGGER_INTERVAL
:canonical: agentsociety.workflow.block.TRIGGER_INTERVAL
:value: >
   1

```{autodoc2-docstring} agentsociety.workflow.block.TRIGGER_INTERVAL
```

````

````{py:function} log_and_check_with_memory(condition: typing.Union[collections.abc.Callable[[agentsociety.memory.Memory], collections.abc.Coroutine[typing.Any, typing.Any, bool]], collections.abc.Callable[[], collections.abc.Coroutine[typing.Any, typing.Any, bool]], collections.abc.Callable[[agentsociety.memory.Memory], bool], collections.abc.Callable[[], bool]] = lambda: True, trigger_interval: float = TRIGGER_INTERVAL, record_function_calling: bool = False)
:canonical: agentsociety.workflow.block.log_and_check_with_memory

```{autodoc2-docstring} agentsociety.workflow.block.log_and_check_with_memory
```
````

````{py:function} log_and_check(condition: typing.Union[collections.abc.Callable[[], collections.abc.Coroutine[typing.Any, typing.Any, bool]], collections.abc.Callable[[], bool]] = lambda: True, trigger_interval: float = TRIGGER_INTERVAL, record_function_calling: bool = False)
:canonical: agentsociety.workflow.block.log_and_check

```{autodoc2-docstring} agentsociety.workflow.block.log_and_check
```
````

````{py:function} trigger_class()
:canonical: agentsociety.workflow.block.trigger_class

```{autodoc2-docstring} agentsociety.workflow.block.trigger_class
```
````

`````{py:class} Block(name: str, llm: typing.Optional[agentsociety.llm.LLM] = None, memory: typing.Optional[agentsociety.memory.Memory] = None, simulator: typing.Optional[agentsociety.environment.simulator.Simulator] = None, trigger: typing.Optional[agentsociety.workflow.trigger.EventTrigger] = None)
:canonical: agentsociety.workflow.block.Block

```{autodoc2-docstring} agentsociety.workflow.block.Block
```

```{rubric} Initialization
```

```{autodoc2-docstring} agentsociety.workflow.block.Block.__init__
```

````{py:attribute} configurable_fields
:canonical: agentsociety.workflow.block.Block.configurable_fields
:type: list[str]
:value: >
   []

```{autodoc2-docstring} agentsociety.workflow.block.Block.configurable_fields
```

````

````{py:attribute} default_values
:canonical: agentsociety.workflow.block.Block.default_values
:type: dict[str, typing.Any]
:value: >
   None

```{autodoc2-docstring} agentsociety.workflow.block.Block.default_values
```

````

````{py:attribute} fields_description
:canonical: agentsociety.workflow.block.Block.fields_description
:type: dict[str, str]
:value: >
   None

```{autodoc2-docstring} agentsociety.workflow.block.Block.fields_description
```

````

````{py:method} export_config() -> dict[str, typing.Optional[str]]
:canonical: agentsociety.workflow.block.Block.export_config

```{autodoc2-docstring} agentsociety.workflow.block.Block.export_config
```

````

````{py:method} export_class_config() -> tuple[dict[str, typing.Any], dict[str, typing.Any]]
:canonical: agentsociety.workflow.block.Block.export_class_config
:classmethod:

```{autodoc2-docstring} agentsociety.workflow.block.Block.export_class_config
```

````

````{py:method} import_config(config: dict[str, typing.Union[str, dict]]) -> agentsociety.workflow.block.Block
:canonical: agentsociety.workflow.block.Block.import_config
:classmethod:

```{autodoc2-docstring} agentsociety.workflow.block.Block.import_config
```

````

````{py:method} load_from_config(config: dict[str, list[dict]]) -> None
:canonical: agentsociety.workflow.block.Block.load_from_config

```{autodoc2-docstring} agentsociety.workflow.block.Block.load_from_config
```

````

````{py:method} forward()
:canonical: agentsociety.workflow.block.Block.forward
:abstractmethod:
:async:

```{autodoc2-docstring} agentsociety.workflow.block.Block.forward
```

````

````{py:property} llm
:canonical: agentsociety.workflow.block.Block.llm
:type: agentsociety.llm.LLM

```{autodoc2-docstring} agentsociety.workflow.block.Block.llm
```

````

````{py:property} memory
:canonical: agentsociety.workflow.block.Block.memory
:type: agentsociety.memory.Memory

```{autodoc2-docstring} agentsociety.workflow.block.Block.memory
```

````

````{py:property} simulator
:canonical: agentsociety.workflow.block.Block.simulator
:type: agentsociety.environment.simulator.Simulator

```{autodoc2-docstring} agentsociety.workflow.block.Block.simulator
```

````

````{py:method} set_llm_client(llm: agentsociety.llm.LLM)
:canonical: agentsociety.workflow.block.Block.set_llm_client

```{autodoc2-docstring} agentsociety.workflow.block.Block.set_llm_client
```

````

````{py:method} set_simulator(simulator: agentsociety.environment.simulator.Simulator)
:canonical: agentsociety.workflow.block.Block.set_simulator

```{autodoc2-docstring} agentsociety.workflow.block.Block.set_simulator
```

````

````{py:method} set_memory(memory: agentsociety.memory.Memory)
:canonical: agentsociety.workflow.block.Block.set_memory

```{autodoc2-docstring} agentsociety.workflow.block.Block.set_memory
```

````

`````
