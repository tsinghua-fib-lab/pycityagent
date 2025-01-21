# {py:mod}`pycityagent.cityagent.blocks.dispatcher`

```{py:module} pycityagent.cityagent.blocks.dispatcher
```

```{autodoc2-docstring} pycityagent.cityagent.blocks.dispatcher
:allowtitles:
```

## Module Contents

### Classes

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`BlockDispatcher <pycityagent.cityagent.blocks.dispatcher.BlockDispatcher>`
  - ```{autodoc2-docstring} pycityagent.cityagent.blocks.dispatcher.BlockDispatcher
    :summary:
    ```
````

### Data

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`logger <pycityagent.cityagent.blocks.dispatcher.logger>`
  - ```{autodoc2-docstring} pycityagent.cityagent.blocks.dispatcher.logger
    :summary:
    ```
* - {py:obj}`DISPATCHER_PROMPT <pycityagent.cityagent.blocks.dispatcher.DISPATCHER_PROMPT>`
  - ```{autodoc2-docstring} pycityagent.cityagent.blocks.dispatcher.DISPATCHER_PROMPT
    :summary:
    ```
````

### API

````{py:data} logger
:canonical: pycityagent.cityagent.blocks.dispatcher.logger
:value: >
   'getLogger(...)'

```{autodoc2-docstring} pycityagent.cityagent.blocks.dispatcher.logger
```

````

````{py:data} DISPATCHER_PROMPT
:canonical: pycityagent.cityagent.blocks.dispatcher.DISPATCHER_PROMPT
:value: <Multiline-String>

```{autodoc2-docstring} pycityagent.cityagent.blocks.dispatcher.DISPATCHER_PROMPT
```

````

`````{py:class} BlockDispatcher(llm: pycityagent.llm.llm.LLM)
:canonical: pycityagent.cityagent.blocks.dispatcher.BlockDispatcher

```{autodoc2-docstring} pycityagent.cityagent.blocks.dispatcher.BlockDispatcher
```

```{rubric} Initialization
```

```{autodoc2-docstring} pycityagent.cityagent.blocks.dispatcher.BlockDispatcher.__init__
```

````{py:method} register_blocks(blocks: typing.List[pycityagent.workflow.block.Block]) -> None
:canonical: pycityagent.cityagent.blocks.dispatcher.BlockDispatcher.register_blocks

```{autodoc2-docstring} pycityagent.cityagent.blocks.dispatcher.BlockDispatcher.register_blocks
```

````

````{py:method} _get_function_schema() -> dict
:canonical: pycityagent.cityagent.blocks.dispatcher.BlockDispatcher._get_function_schema

```{autodoc2-docstring} pycityagent.cityagent.blocks.dispatcher.BlockDispatcher._get_function_schema
```

````

````{py:method} dispatch(step: dict) -> pycityagent.workflow.block.Block
:canonical: pycityagent.cityagent.blocks.dispatcher.BlockDispatcher.dispatch
:async:

```{autodoc2-docstring} pycityagent.cityagent.blocks.dispatcher.BlockDispatcher.dispatch
```

````

`````
