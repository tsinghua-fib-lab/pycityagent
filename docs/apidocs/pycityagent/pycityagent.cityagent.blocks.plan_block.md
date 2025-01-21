# {py:mod}`pycityagent.cityagent.blocks.plan_block`

```{py:module} pycityagent.cityagent.blocks.plan_block
```

```{autodoc2-docstring} pycityagent.cityagent.blocks.plan_block
:allowtitles:
```

## Module Contents

### Classes

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`PlanBlock <pycityagent.cityagent.blocks.plan_block.PlanBlock>`
  - ```{autodoc2-docstring} pycityagent.cityagent.blocks.plan_block.PlanBlock
    :summary:
    ```
````

### Data

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`logger <pycityagent.cityagent.blocks.plan_block.logger>`
  - ```{autodoc2-docstring} pycityagent.cityagent.blocks.plan_block.logger
    :summary:
    ```
* - {py:obj}`GUIDANCE_SELECTION_PROMPT <pycityagent.cityagent.blocks.plan_block.GUIDANCE_SELECTION_PROMPT>`
  - ```{autodoc2-docstring} pycityagent.cityagent.blocks.plan_block.GUIDANCE_SELECTION_PROMPT
    :summary:
    ```
* - {py:obj}`DETAILED_PLAN_PROMPT <pycityagent.cityagent.blocks.plan_block.DETAILED_PLAN_PROMPT>`
  - ```{autodoc2-docstring} pycityagent.cityagent.blocks.plan_block.DETAILED_PLAN_PROMPT
    :summary:
    ```
````

### API

````{py:data} logger
:canonical: pycityagent.cityagent.blocks.plan_block.logger
:value: >
   'getLogger(...)'

```{autodoc2-docstring} pycityagent.cityagent.blocks.plan_block.logger
```

````

````{py:data} GUIDANCE_SELECTION_PROMPT
:canonical: pycityagent.cityagent.blocks.plan_block.GUIDANCE_SELECTION_PROMPT
:value: <Multiline-String>

```{autodoc2-docstring} pycityagent.cityagent.blocks.plan_block.GUIDANCE_SELECTION_PROMPT
```

````

````{py:data} DETAILED_PLAN_PROMPT
:canonical: pycityagent.cityagent.blocks.plan_block.DETAILED_PLAN_PROMPT
:value: <Multiline-String>

```{autodoc2-docstring} pycityagent.cityagent.blocks.plan_block.DETAILED_PLAN_PROMPT
```

````

`````{py:class} PlanBlock(llm: pycityagent.llm.LLM, memory: pycityagent.memory.Memory, simulator: pycityagent.environment.simulator.Simulator)
:canonical: pycityagent.cityagent.blocks.plan_block.PlanBlock

Bases: {py:obj}`pycityagent.workflow.Block`

```{autodoc2-docstring} pycityagent.cityagent.blocks.plan_block.PlanBlock
```

```{rubric} Initialization
```

```{autodoc2-docstring} pycityagent.cityagent.blocks.plan_block.PlanBlock.__init__
```

````{py:attribute} configurable_fields
:canonical: pycityagent.cityagent.blocks.plan_block.PlanBlock.configurable_fields
:type: typing.List[str]
:value: >
   ['max_plan_steps']

```{autodoc2-docstring} pycityagent.cityagent.blocks.plan_block.PlanBlock.configurable_fields
```

````

````{py:attribute} default_values
:canonical: pycityagent.cityagent.blocks.plan_block.PlanBlock.default_values
:value: >
   None

```{autodoc2-docstring} pycityagent.cityagent.blocks.plan_block.PlanBlock.default_values
```

````

````{py:attribute} fields_description
:canonical: pycityagent.cityagent.blocks.plan_block.PlanBlock.fields_description
:value: >
   None

```{autodoc2-docstring} pycityagent.cityagent.blocks.plan_block.PlanBlock.fields_description
```

````

````{py:method} select_guidance(current_need: str) -> typing.Dict
:canonical: pycityagent.cityagent.blocks.plan_block.PlanBlock.select_guidance
:async:

```{autodoc2-docstring} pycityagent.cityagent.blocks.plan_block.PlanBlock.select_guidance
```

````

````{py:method} generate_detailed_plan(current_need: str, selected_option: str) -> typing.Dict
:canonical: pycityagent.cityagent.blocks.plan_block.PlanBlock.generate_detailed_plan
:async:

```{autodoc2-docstring} pycityagent.cityagent.blocks.plan_block.PlanBlock.generate_detailed_plan
```

````

````{py:method} forward()
:canonical: pycityagent.cityagent.blocks.plan_block.PlanBlock.forward
:async:

````

````{py:method} clean_json_response(response: str) -> str
:canonical: pycityagent.cityagent.blocks.plan_block.PlanBlock.clean_json_response

```{autodoc2-docstring} pycityagent.cityagent.blocks.plan_block.PlanBlock.clean_json_response
```

````

`````
