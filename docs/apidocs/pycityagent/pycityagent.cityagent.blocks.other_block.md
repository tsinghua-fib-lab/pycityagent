# {py:mod}`pycityagent.cityagent.blocks.other_block`

```{py:module} pycityagent.cityagent.blocks.other_block
```

```{autodoc2-docstring} pycityagent.cityagent.blocks.other_block
:allowtitles:
```

## Module Contents

### Classes

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`SleepBlock <pycityagent.cityagent.blocks.other_block.SleepBlock>`
  - ```{autodoc2-docstring} pycityagent.cityagent.blocks.other_block.SleepBlock
    :summary:
    ```
* - {py:obj}`OtherNoneBlock <pycityagent.cityagent.blocks.other_block.OtherNoneBlock>`
  - ```{autodoc2-docstring} pycityagent.cityagent.blocks.other_block.OtherNoneBlock
    :summary:
    ```
* - {py:obj}`OtherBlock <pycityagent.cityagent.blocks.other_block.OtherBlock>`
  - ```{autodoc2-docstring} pycityagent.cityagent.blocks.other_block.OtherBlock
    :summary:
    ```
````

### Data

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`logger <pycityagent.cityagent.blocks.other_block.logger>`
  - ```{autodoc2-docstring} pycityagent.cityagent.blocks.other_block.logger
    :summary:
    ```
````

### API

````{py:data} logger
:canonical: pycityagent.cityagent.blocks.other_block.logger
:value: >
   'getLogger(...)'

```{autodoc2-docstring} pycityagent.cityagent.blocks.other_block.logger
```

````

`````{py:class} SleepBlock(llm: pycityagent.llm.llm.LLM, memory: pycityagent.memory.Memory)
:canonical: pycityagent.cityagent.blocks.other_block.SleepBlock

Bases: {py:obj}`pycityagent.workflow.block.Block`

```{autodoc2-docstring} pycityagent.cityagent.blocks.other_block.SleepBlock
```

```{rubric} Initialization
```

```{autodoc2-docstring} pycityagent.cityagent.blocks.other_block.SleepBlock.__init__
```

````{py:method} forward(step, context)
:canonical: pycityagent.cityagent.blocks.other_block.SleepBlock.forward
:async:

````

`````

`````{py:class} OtherNoneBlock(llm: pycityagent.llm.llm.LLM, memory: pycityagent.memory.Memory)
:canonical: pycityagent.cityagent.blocks.other_block.OtherNoneBlock

Bases: {py:obj}`pycityagent.workflow.block.Block`

```{autodoc2-docstring} pycityagent.cityagent.blocks.other_block.OtherNoneBlock
```

```{rubric} Initialization
```

```{autodoc2-docstring} pycityagent.cityagent.blocks.other_block.OtherNoneBlock.__init__
```

````{py:method} forward(step, context)
:canonical: pycityagent.cityagent.blocks.other_block.OtherNoneBlock.forward
:async:

````

`````

`````{py:class} OtherBlock(llm: pycityagent.llm.llm.LLM, memory: pycityagent.memory.Memory)
:canonical: pycityagent.cityagent.blocks.other_block.OtherBlock

Bases: {py:obj}`pycityagent.workflow.block.Block`

```{autodoc2-docstring} pycityagent.cityagent.blocks.other_block.OtherBlock
```

```{rubric} Initialization
```

```{autodoc2-docstring} pycityagent.cityagent.blocks.other_block.OtherBlock.__init__
```

````{py:attribute} sleep_block
:canonical: pycityagent.cityagent.blocks.other_block.OtherBlock.sleep_block
:type: pycityagent.cityagent.blocks.other_block.SleepBlock
:value: >
   None

```{autodoc2-docstring} pycityagent.cityagent.blocks.other_block.OtherBlock.sleep_block
```

````

````{py:attribute} other_none_block
:canonical: pycityagent.cityagent.blocks.other_block.OtherBlock.other_none_block
:type: pycityagent.cityagent.blocks.other_block.OtherNoneBlock
:value: >
   None

```{autodoc2-docstring} pycityagent.cityagent.blocks.other_block.OtherBlock.other_none_block
```

````

````{py:method} forward(step, context)
:canonical: pycityagent.cityagent.blocks.other_block.OtherBlock.forward
:async:

````

`````
