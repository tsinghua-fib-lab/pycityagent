# {py:mod}`agentsociety.cityagent.blocks.economy_block`

```{py:module} agentsociety.cityagent.blocks.economy_block
```

```{autodoc2-docstring} agentsociety.cityagent.blocks.economy_block
:allowtitles:
```

## Module Contents

### Classes

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`WorkBlock <agentsociety.cityagent.blocks.economy_block.WorkBlock>`
  - ```{autodoc2-docstring} agentsociety.cityagent.blocks.economy_block.WorkBlock
    :summary:
    ```
* - {py:obj}`ConsumptionBlock <agentsociety.cityagent.blocks.economy_block.ConsumptionBlock>`
  - ```{autodoc2-docstring} agentsociety.cityagent.blocks.economy_block.ConsumptionBlock
    :summary:
    ```
* - {py:obj}`EconomyNoneBlock <agentsociety.cityagent.blocks.economy_block.EconomyNoneBlock>`
  - ```{autodoc2-docstring} agentsociety.cityagent.blocks.economy_block.EconomyNoneBlock
    :summary:
    ```
* - {py:obj}`EconomyBlock <agentsociety.cityagent.blocks.economy_block.EconomyBlock>`
  -
* - {py:obj}`MonthPlanBlock <agentsociety.cityagent.blocks.economy_block.MonthPlanBlock>`
  - ```{autodoc2-docstring} agentsociety.cityagent.blocks.economy_block.MonthPlanBlock
    :summary:
    ```
````

### Functions

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`softmax <agentsociety.cityagent.blocks.economy_block.softmax>`
  - ```{autodoc2-docstring} agentsociety.cityagent.blocks.economy_block.softmax
    :summary:
    ```
````

### Data

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`logger <agentsociety.cityagent.blocks.economy_block.logger>`
  - ```{autodoc2-docstring} agentsociety.cityagent.blocks.economy_block.logger
    :summary:
    ```
````

### API

````{py:data} logger
:canonical: agentsociety.cityagent.blocks.economy_block.logger
:value: >
   'getLogger(...)'

```{autodoc2-docstring} agentsociety.cityagent.blocks.economy_block.logger
```

````

````{py:function} softmax(x, gamma=1.0)
:canonical: agentsociety.cityagent.blocks.economy_block.softmax

```{autodoc2-docstring} agentsociety.cityagent.blocks.economy_block.softmax
```
````

`````{py:class} WorkBlock(llm: agentsociety.llm.llm.LLM, memory: agentsociety.memory.Memory, simulator: agentsociety.environment.simulator.Simulator)
:canonical: agentsociety.cityagent.blocks.economy_block.WorkBlock

Bases: {py:obj}`agentsociety.workflow.block.Block`

```{autodoc2-docstring} agentsociety.cityagent.blocks.economy_block.WorkBlock
```

```{rubric} Initialization
```

```{autodoc2-docstring} agentsociety.cityagent.blocks.economy_block.WorkBlock.__init__
```

````{py:method} forward(step, context)
:canonical: agentsociety.cityagent.blocks.economy_block.WorkBlock.forward
:async:

````

`````

`````{py:class} ConsumptionBlock(llm: agentsociety.llm.llm.LLM, memory: agentsociety.memory.Memory, simulator: agentsociety.environment.simulator.Simulator, economy_client: agentsociety.environment.EconomyClient)
:canonical: agentsociety.cityagent.blocks.economy_block.ConsumptionBlock

Bases: {py:obj}`agentsociety.workflow.block.Block`

```{autodoc2-docstring} agentsociety.cityagent.blocks.economy_block.ConsumptionBlock
```

```{rubric} Initialization
```

```{autodoc2-docstring} agentsociety.cityagent.blocks.economy_block.ConsumptionBlock.__init__
```

````{py:method} forward(step, context)
:canonical: agentsociety.cityagent.blocks.economy_block.ConsumptionBlock.forward
:async:

````

`````

`````{py:class} EconomyNoneBlock(llm: agentsociety.llm.llm.LLM, memory: agentsociety.memory.Memory)
:canonical: agentsociety.cityagent.blocks.economy_block.EconomyNoneBlock

Bases: {py:obj}`agentsociety.workflow.block.Block`

```{autodoc2-docstring} agentsociety.cityagent.blocks.economy_block.EconomyNoneBlock
```

```{rubric} Initialization
```

```{autodoc2-docstring} agentsociety.cityagent.blocks.economy_block.EconomyNoneBlock.__init__
```

````{py:method} forward(step, context)
:canonical: agentsociety.cityagent.blocks.economy_block.EconomyNoneBlock.forward
:async:

````

`````

`````{py:class} EconomyBlock(llm: agentsociety.llm.llm.LLM, memory: agentsociety.memory.Memory, simulator: agentsociety.environment.simulator.Simulator, economy_client: agentsociety.environment.EconomyClient)
:canonical: agentsociety.cityagent.blocks.economy_block.EconomyBlock

Bases: {py:obj}`agentsociety.workflow.block.Block`

````{py:attribute} work_block
:canonical: agentsociety.cityagent.blocks.economy_block.EconomyBlock.work_block
:type: agentsociety.cityagent.blocks.economy_block.WorkBlock
:value: >
   None

```{autodoc2-docstring} agentsociety.cityagent.blocks.economy_block.EconomyBlock.work_block
```

````

````{py:attribute} consumption_block
:canonical: agentsociety.cityagent.blocks.economy_block.EconomyBlock.consumption_block
:type: agentsociety.cityagent.blocks.economy_block.ConsumptionBlock
:value: >
   None

```{autodoc2-docstring} agentsociety.cityagent.blocks.economy_block.EconomyBlock.consumption_block
```

````

````{py:attribute} none_block
:canonical: agentsociety.cityagent.blocks.economy_block.EconomyBlock.none_block
:type: agentsociety.cityagent.blocks.economy_block.EconomyNoneBlock
:value: >
   None

```{autodoc2-docstring} agentsociety.cityagent.blocks.economy_block.EconomyBlock.none_block
```

````

````{py:method} forward(step, context)
:canonical: agentsociety.cityagent.blocks.economy_block.EconomyBlock.forward
:async:

````

`````

`````{py:class} MonthPlanBlock(llm: agentsociety.llm.llm.LLM, memory: agentsociety.memory.Memory, simulator: agentsociety.environment.simulator.Simulator, economy_client: agentsociety.environment.EconomyClient)
:canonical: agentsociety.cityagent.blocks.economy_block.MonthPlanBlock

Bases: {py:obj}`agentsociety.workflow.block.Block`

```{autodoc2-docstring} agentsociety.cityagent.blocks.economy_block.MonthPlanBlock
```

```{rubric} Initialization
```

```{autodoc2-docstring} agentsociety.cityagent.blocks.economy_block.MonthPlanBlock.__init__
```

````{py:attribute} configurable_fields
:canonical: agentsociety.cityagent.blocks.economy_block.MonthPlanBlock.configurable_fields
:value: >
   ['UBI', 'num_labor_hours', 'productivity_per_labor', 'time_diff']

```{autodoc2-docstring} agentsociety.cityagent.blocks.economy_block.MonthPlanBlock.configurable_fields
```

````

````{py:attribute} default_values
:canonical: agentsociety.cityagent.blocks.economy_block.MonthPlanBlock.default_values
:value: >
   None

```{autodoc2-docstring} agentsociety.cityagent.blocks.economy_block.MonthPlanBlock.default_values
```

````

````{py:attribute} fields_description
:canonical: agentsociety.cityagent.blocks.economy_block.MonthPlanBlock.fields_description
:value: >
   None

```{autodoc2-docstring} agentsociety.cityagent.blocks.economy_block.MonthPlanBlock.fields_description
```

````

````{py:method} month_trigger()
:canonical: agentsociety.cityagent.blocks.economy_block.MonthPlanBlock.month_trigger
:async:

```{autodoc2-docstring} agentsociety.cityagent.blocks.economy_block.MonthPlanBlock.month_trigger
```

````

````{py:method} forward()
:canonical: agentsociety.cityagent.blocks.economy_block.MonthPlanBlock.forward
:async:

````

`````
