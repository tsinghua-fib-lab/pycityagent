# {py:mod}`agentsociety.cityagent.blocks.plan_block`

```{py:module} agentsociety.cityagent.blocks.plan_block
```

```{autodoc2-docstring} agentsociety.cityagent.blocks.plan_block
:allowtitles:
```

## Module Contents

### Classes

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`PlanBlock <agentsociety.cityagent.blocks.plan_block.PlanBlock>`
  -
````

### Data

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`logger <agentsociety.cityagent.blocks.plan_block.logger>`
  - ```{autodoc2-docstring} agentsociety.cityagent.blocks.plan_block.logger
    :summary:
    ```
* - {py:obj}`GUIDANCE_SELECTION_PROMPT <agentsociety.cityagent.blocks.plan_block.GUIDANCE_SELECTION_PROMPT>`
  - ```{autodoc2-docstring} agentsociety.cityagent.blocks.plan_block.GUIDANCE_SELECTION_PROMPT
    :summary:
    ```
* - {py:obj}`DETAILED_PLAN_PROMPT <agentsociety.cityagent.blocks.plan_block.DETAILED_PLAN_PROMPT>`
  - ```{autodoc2-docstring} agentsociety.cityagent.blocks.plan_block.DETAILED_PLAN_PROMPT
    :summary:
    ```
````

### API

````{py:data} logger
:canonical: agentsociety.cityagent.blocks.plan_block.logger
:value: >
   'getLogger(...)'

```{autodoc2-docstring} agentsociety.cityagent.blocks.plan_block.logger
```

````

````{py:data} GUIDANCE_SELECTION_PROMPT
:canonical: agentsociety.cityagent.blocks.plan_block.GUIDANCE_SELECTION_PROMPT
:value: <Multiline-String>

```{autodoc2-docstring} agentsociety.cityagent.blocks.plan_block.GUIDANCE_SELECTION_PROMPT
```

````

````{py:data} DETAILED_PLAN_PROMPT
:canonical: agentsociety.cityagent.blocks.plan_block.DETAILED_PLAN_PROMPT
:value: <Multiline-String>

```{autodoc2-docstring} agentsociety.cityagent.blocks.plan_block.DETAILED_PLAN_PROMPT
```

````

`````{py:class} PlanBlock(llm: agentsociety.llm.LLM, memory: agentsociety.memory.Memory, simulator: agentsociety.environment.simulator.Simulator)
:canonical: agentsociety.cityagent.blocks.plan_block.PlanBlock

Bases: {py:obj}`agentsociety.workflow.Block`

````{py:attribute} configurable_fields
:canonical: agentsociety.cityagent.blocks.plan_block.PlanBlock.configurable_fields
:type: typing.List[str]
:value: >
   ['max_plan_steps']

```{autodoc2-docstring} agentsociety.cityagent.blocks.plan_block.PlanBlock.configurable_fields
```

````

````{py:attribute} default_values
:canonical: agentsociety.cityagent.blocks.plan_block.PlanBlock.default_values
:value: >
   None

```{autodoc2-docstring} agentsociety.cityagent.blocks.plan_block.PlanBlock.default_values
```

````

````{py:attribute} fields_description
:canonical: agentsociety.cityagent.blocks.plan_block.PlanBlock.fields_description
:value: >
   None

```{autodoc2-docstring} agentsociety.cityagent.blocks.plan_block.PlanBlock.fields_description
```

````

````{py:method} select_guidance(current_need: str) -> typing.Dict
:canonical: agentsociety.cityagent.blocks.plan_block.PlanBlock.select_guidance
:async:

```{autodoc2-docstring} agentsociety.cityagent.blocks.plan_block.PlanBlock.select_guidance
```

````

````{py:method} generate_detailed_plan(selected_option: str) -> typing.Dict
:canonical: agentsociety.cityagent.blocks.plan_block.PlanBlock.generate_detailed_plan
:async:

```{autodoc2-docstring} agentsociety.cityagent.blocks.plan_block.PlanBlock.generate_detailed_plan
```

````

````{py:method} forward()
:canonical: agentsociety.cityagent.blocks.plan_block.PlanBlock.forward
:async:

````

`````
