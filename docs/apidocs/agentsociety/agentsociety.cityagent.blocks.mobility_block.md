# {py:mod}`agentsociety.cityagent.blocks.mobility_block`

```{py:module} agentsociety.cityagent.blocks.mobility_block
```

```{autodoc2-docstring} agentsociety.cityagent.blocks.mobility_block
:allowtitles:
```

## Module Contents

### Classes

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`PlaceSelectionBlock <agentsociety.cityagent.blocks.mobility_block.PlaceSelectionBlock>`
  - ```{autodoc2-docstring} agentsociety.cityagent.blocks.mobility_block.PlaceSelectionBlock
    :summary:
    ```
* - {py:obj}`MoveBlock <agentsociety.cityagent.blocks.mobility_block.MoveBlock>`
  - ```{autodoc2-docstring} agentsociety.cityagent.blocks.mobility_block.MoveBlock
    :summary:
    ```
* - {py:obj}`MobilityNoneBlock <agentsociety.cityagent.blocks.mobility_block.MobilityNoneBlock>`
  - ```{autodoc2-docstring} agentsociety.cityagent.blocks.mobility_block.MobilityNoneBlock
    :summary:
    ```
* - {py:obj}`MobilityBlock <agentsociety.cityagent.blocks.mobility_block.MobilityBlock>`
  -
````

### Functions

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`gravity_model <agentsociety.cityagent.blocks.mobility_block.gravity_model>`
  - ```{autodoc2-docstring} agentsociety.cityagent.blocks.mobility_block.gravity_model
    :summary:
    ```
````

### Data

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`logger <agentsociety.cityagent.blocks.mobility_block.logger>`
  - ```{autodoc2-docstring} agentsociety.cityagent.blocks.mobility_block.logger
    :summary:
    ```
* - {py:obj}`PLACE_TYPE_SELECTION_PROMPT <agentsociety.cityagent.blocks.mobility_block.PLACE_TYPE_SELECTION_PROMPT>`
  - ```{autodoc2-docstring} agentsociety.cityagent.blocks.mobility_block.PLACE_TYPE_SELECTION_PROMPT
    :summary:
    ```
* - {py:obj}`PLACE_SECOND_TYPE_SELECTION_PROMPT <agentsociety.cityagent.blocks.mobility_block.PLACE_SECOND_TYPE_SELECTION_PROMPT>`
  - ```{autodoc2-docstring} agentsociety.cityagent.blocks.mobility_block.PLACE_SECOND_TYPE_SELECTION_PROMPT
    :summary:
    ```
* - {py:obj}`PLACE_ANALYSIS_PROMPT <agentsociety.cityagent.blocks.mobility_block.PLACE_ANALYSIS_PROMPT>`
  - ```{autodoc2-docstring} agentsociety.cityagent.blocks.mobility_block.PLACE_ANALYSIS_PROMPT
    :summary:
    ```
* - {py:obj}`RADIUS_PROMPT <agentsociety.cityagent.blocks.mobility_block.RADIUS_PROMPT>`
  - ```{autodoc2-docstring} agentsociety.cityagent.blocks.mobility_block.RADIUS_PROMPT
    :summary:
    ```
````

### API

````{py:data} logger
:canonical: agentsociety.cityagent.blocks.mobility_block.logger
:value: >
   'getLogger(...)'

```{autodoc2-docstring} agentsociety.cityagent.blocks.mobility_block.logger
```

````

````{py:data} PLACE_TYPE_SELECTION_PROMPT
:canonical: agentsociety.cityagent.blocks.mobility_block.PLACE_TYPE_SELECTION_PROMPT
:value: <Multiline-String>

```{autodoc2-docstring} agentsociety.cityagent.blocks.mobility_block.PLACE_TYPE_SELECTION_PROMPT
```

````

````{py:data} PLACE_SECOND_TYPE_SELECTION_PROMPT
:canonical: agentsociety.cityagent.blocks.mobility_block.PLACE_SECOND_TYPE_SELECTION_PROMPT
:value: <Multiline-String>

```{autodoc2-docstring} agentsociety.cityagent.blocks.mobility_block.PLACE_SECOND_TYPE_SELECTION_PROMPT
```

````

````{py:data} PLACE_ANALYSIS_PROMPT
:canonical: agentsociety.cityagent.blocks.mobility_block.PLACE_ANALYSIS_PROMPT
:value: <Multiline-String>

```{autodoc2-docstring} agentsociety.cityagent.blocks.mobility_block.PLACE_ANALYSIS_PROMPT
```

````

````{py:data} RADIUS_PROMPT
:canonical: agentsociety.cityagent.blocks.mobility_block.RADIUS_PROMPT
:value: <Multiline-String>

```{autodoc2-docstring} agentsociety.cityagent.blocks.mobility_block.RADIUS_PROMPT
```

````

````{py:function} gravity_model(pois)
:canonical: agentsociety.cityagent.blocks.mobility_block.gravity_model

```{autodoc2-docstring} agentsociety.cityagent.blocks.mobility_block.gravity_model
```
````

`````{py:class} PlaceSelectionBlock(llm: agentsociety.llm.LLM, memory: agentsociety.memory.Memory, simulator: agentsociety.environment.simulator.Simulator)
:canonical: agentsociety.cityagent.blocks.mobility_block.PlaceSelectionBlock

Bases: {py:obj}`agentsociety.workflow.block.Block`

```{autodoc2-docstring} agentsociety.cityagent.blocks.mobility_block.PlaceSelectionBlock
```

```{rubric} Initialization
```

```{autodoc2-docstring} agentsociety.cityagent.blocks.mobility_block.PlaceSelectionBlock.__init__
```

````{py:attribute} configurable_fields
:canonical: agentsociety.cityagent.blocks.mobility_block.PlaceSelectionBlock.configurable_fields
:type: typing.List[str]
:value: >
   ['search_limit']

```{autodoc2-docstring} agentsociety.cityagent.blocks.mobility_block.PlaceSelectionBlock.configurable_fields
```

````

````{py:attribute} default_values
:canonical: agentsociety.cityagent.blocks.mobility_block.PlaceSelectionBlock.default_values
:value: >
   None

```{autodoc2-docstring} agentsociety.cityagent.blocks.mobility_block.PlaceSelectionBlock.default_values
```

````

````{py:method} forward(step, context)
:canonical: agentsociety.cityagent.blocks.mobility_block.PlaceSelectionBlock.forward
:async:

````

`````

`````{py:class} MoveBlock(llm: agentsociety.llm.LLM, memory: agentsociety.memory.Memory, simulator: agentsociety.environment.simulator.Simulator)
:canonical: agentsociety.cityagent.blocks.mobility_block.MoveBlock

Bases: {py:obj}`agentsociety.workflow.block.Block`

```{autodoc2-docstring} agentsociety.cityagent.blocks.mobility_block.MoveBlock
```

```{rubric} Initialization
```

```{autodoc2-docstring} agentsociety.cityagent.blocks.mobility_block.MoveBlock.__init__
```

````{py:method} forward(step, context)
:canonical: agentsociety.cityagent.blocks.mobility_block.MoveBlock.forward
:async:

````

`````

`````{py:class} MobilityNoneBlock(llm: agentsociety.llm.LLM, memory: agentsociety.memory.Memory)
:canonical: agentsociety.cityagent.blocks.mobility_block.MobilityNoneBlock

Bases: {py:obj}`agentsociety.workflow.block.Block`

```{autodoc2-docstring} agentsociety.cityagent.blocks.mobility_block.MobilityNoneBlock
```

```{rubric} Initialization
```

```{autodoc2-docstring} agentsociety.cityagent.blocks.mobility_block.MobilityNoneBlock.__init__
```

````{py:method} forward(step, context)
:canonical: agentsociety.cityagent.blocks.mobility_block.MobilityNoneBlock.forward
:async:

````

`````

`````{py:class} MobilityBlock(llm: agentsociety.llm.LLM, memory: agentsociety.memory.Memory, simulator: agentsociety.environment.simulator.Simulator)
:canonical: agentsociety.cityagent.blocks.mobility_block.MobilityBlock

Bases: {py:obj}`agentsociety.workflow.block.Block`

````{py:attribute} place_selection_block
:canonical: agentsociety.cityagent.blocks.mobility_block.MobilityBlock.place_selection_block
:type: agentsociety.cityagent.blocks.mobility_block.PlaceSelectionBlock
:value: >
   None

```{autodoc2-docstring} agentsociety.cityagent.blocks.mobility_block.MobilityBlock.place_selection_block
```

````

````{py:attribute} move_block
:canonical: agentsociety.cityagent.blocks.mobility_block.MobilityBlock.move_block
:type: agentsociety.cityagent.blocks.mobility_block.MoveBlock
:value: >
   None

```{autodoc2-docstring} agentsociety.cityagent.blocks.mobility_block.MobilityBlock.move_block
```

````

````{py:attribute} mobility_none_block
:canonical: agentsociety.cityagent.blocks.mobility_block.MobilityBlock.mobility_none_block
:type: agentsociety.cityagent.blocks.mobility_block.MobilityNoneBlock
:value: >
   None

```{autodoc2-docstring} agentsociety.cityagent.blocks.mobility_block.MobilityBlock.mobility_none_block
```

````

````{py:method} forward(step, context)
:canonical: agentsociety.cityagent.blocks.mobility_block.MobilityBlock.forward
:async:

````

`````
