# {py:mod}`agentsociety.cityagent.blocks.dispatcher`

```{py:module} agentsociety.cityagent.blocks.dispatcher
```

```{autodoc2-docstring} agentsociety.cityagent.blocks.dispatcher
:allowtitles:
```

## Module Contents

### Classes

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`BlockDispatcher <agentsociety.cityagent.blocks.dispatcher.BlockDispatcher>`
  - ```{autodoc2-docstring} agentsociety.cityagent.blocks.dispatcher.BlockDispatcher
    :summary:
    ```
````

### Data

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`logger <agentsociety.cityagent.blocks.dispatcher.logger>`
  - ```{autodoc2-docstring} agentsociety.cityagent.blocks.dispatcher.logger
    :summary:
    ```
* - {py:obj}`DISPATCHER_PROMPT <agentsociety.cityagent.blocks.dispatcher.DISPATCHER_PROMPT>`
  - ```{autodoc2-docstring} agentsociety.cityagent.blocks.dispatcher.DISPATCHER_PROMPT
    :summary:
    ```
````

### API

````{py:data} logger
:canonical: agentsociety.cityagent.blocks.dispatcher.logger
:value: >
   'getLogger(...)'

```{autodoc2-docstring} agentsociety.cityagent.blocks.dispatcher.logger
```

````

````{py:data} DISPATCHER_PROMPT
:canonical: agentsociety.cityagent.blocks.dispatcher.DISPATCHER_PROMPT
:value: <Multiline-String>

```{autodoc2-docstring} agentsociety.cityagent.blocks.dispatcher.DISPATCHER_PROMPT
```

````

`````{py:class} BlockDispatcher(llm: agentsociety.llm.llm.LLM)
:canonical: agentsociety.cityagent.blocks.dispatcher.BlockDispatcher

```{autodoc2-docstring} agentsociety.cityagent.blocks.dispatcher.BlockDispatcher
```

```{rubric} Initialization
```

```{autodoc2-docstring} agentsociety.cityagent.blocks.dispatcher.BlockDispatcher.__init__
```

````{py:method} register_blocks(blocks: typing.List[agentsociety.workflow.block.Block]) -> None
:canonical: agentsociety.cityagent.blocks.dispatcher.BlockDispatcher.register_blocks

```{autodoc2-docstring} agentsociety.cityagent.blocks.dispatcher.BlockDispatcher.register_blocks
```

````

````{py:method} _get_function_schema() -> dict
:canonical: agentsociety.cityagent.blocks.dispatcher.BlockDispatcher._get_function_schema

```{autodoc2-docstring} agentsociety.cityagent.blocks.dispatcher.BlockDispatcher._get_function_schema
```

````

````{py:method} dispatch(step: dict) -> agentsociety.workflow.block.Block
:canonical: agentsociety.cityagent.blocks.dispatcher.BlockDispatcher.dispatch
:async:

```{autodoc2-docstring} agentsociety.cityagent.blocks.dispatcher.BlockDispatcher.dispatch
```

````

`````
