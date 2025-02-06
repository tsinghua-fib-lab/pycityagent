# {py:mod}`agentsociety.cityagent.blocks.other_block`

```{py:module} agentsociety.cityagent.blocks.other_block
```

```{autodoc2-docstring} agentsociety.cityagent.blocks.other_block
:allowtitles:
```

## Module Contents

### Classes

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`SleepBlock <agentsociety.cityagent.blocks.other_block.SleepBlock>`
  -
* - {py:obj}`OtherNoneBlock <agentsociety.cityagent.blocks.other_block.OtherNoneBlock>`
  - ```{autodoc2-docstring} agentsociety.cityagent.blocks.other_block.OtherNoneBlock
    :summary:
    ```
* - {py:obj}`OtherBlock <agentsociety.cityagent.blocks.other_block.OtherBlock>`
  -
````

### Data

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`logger <agentsociety.cityagent.blocks.other_block.logger>`
  - ```{autodoc2-docstring} agentsociety.cityagent.blocks.other_block.logger
    :summary:
    ```
````

### API

````{py:data} logger
:canonical: agentsociety.cityagent.blocks.other_block.logger
:value: >
   'getLogger(...)'

```{autodoc2-docstring} agentsociety.cityagent.blocks.other_block.logger
```

````

`````{py:class} SleepBlock(llm: agentsociety.llm.llm.LLM, memory: agentsociety.memory.Memory)
:canonical: agentsociety.cityagent.blocks.other_block.SleepBlock

Bases: {py:obj}`agentsociety.workflow.block.Block`

````{py:method} forward(step, context)
:canonical: agentsociety.cityagent.blocks.other_block.SleepBlock.forward
:async:

````

`````

`````{py:class} OtherNoneBlock(llm: agentsociety.llm.llm.LLM, memory: agentsociety.memory.Memory)
:canonical: agentsociety.cityagent.blocks.other_block.OtherNoneBlock

Bases: {py:obj}`agentsociety.workflow.block.Block`

```{autodoc2-docstring} agentsociety.cityagent.blocks.other_block.OtherNoneBlock
```

```{rubric} Initialization
```

```{autodoc2-docstring} agentsociety.cityagent.blocks.other_block.OtherNoneBlock.__init__
```

````{py:method} forward(step, context)
:canonical: agentsociety.cityagent.blocks.other_block.OtherNoneBlock.forward
:async:

````

`````

`````{py:class} OtherBlock(llm: agentsociety.llm.llm.LLM, memory: agentsociety.memory.Memory)
:canonical: agentsociety.cityagent.blocks.other_block.OtherBlock

Bases: {py:obj}`agentsociety.workflow.block.Block`

````{py:attribute} sleep_block
:canonical: agentsociety.cityagent.blocks.other_block.OtherBlock.sleep_block
:type: agentsociety.cityagent.blocks.other_block.SleepBlock
:value: >
   None

```{autodoc2-docstring} agentsociety.cityagent.blocks.other_block.OtherBlock.sleep_block
```

````

````{py:attribute} other_none_block
:canonical: agentsociety.cityagent.blocks.other_block.OtherBlock.other_none_block
:type: agentsociety.cityagent.blocks.other_block.OtherNoneBlock
:value: >
   None

```{autodoc2-docstring} agentsociety.cityagent.blocks.other_block.OtherBlock.other_none_block
```

````

````{py:method} forward(step, context)
:canonical: agentsociety.cityagent.blocks.other_block.OtherBlock.forward
:async:

````

`````
