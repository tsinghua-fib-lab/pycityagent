# {py:mod}`agentsociety.cityagent.blocks.cognition_block`

```{py:module} agentsociety.cityagent.blocks.cognition_block
```

```{autodoc2-docstring} agentsociety.cityagent.blocks.cognition_block
:allowtitles:
```

## Module Contents

### Classes

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`CognitionBlock <agentsociety.cityagent.blocks.cognition_block.CognitionBlock>`
  -
````

### Functions

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`extract_json <agentsociety.cityagent.blocks.cognition_block.extract_json>`
  - ```{autodoc2-docstring} agentsociety.cityagent.blocks.cognition_block.extract_json
    :summary:
    ```
````

### Data

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`logger <agentsociety.cityagent.blocks.cognition_block.logger>`
  - ```{autodoc2-docstring} agentsociety.cityagent.blocks.cognition_block.logger
    :summary:
    ```
````

### API

````{py:data} logger
:canonical: agentsociety.cityagent.blocks.cognition_block.logger
:value: >
   'getLogger(...)'

```{autodoc2-docstring} agentsociety.cityagent.blocks.cognition_block.logger
```

````

````{py:function} extract_json(output_str)
:canonical: agentsociety.cityagent.blocks.cognition_block.extract_json

```{autodoc2-docstring} agentsociety.cityagent.blocks.cognition_block.extract_json
```
````

`````{py:class} CognitionBlock(llm: agentsociety.llm.LLM, memory: agentsociety.memory.Memory, simulator: agentsociety.environment.simulator.Simulator)
:canonical: agentsociety.cityagent.blocks.cognition_block.CognitionBlock

Bases: {py:obj}`agentsociety.workflow.block.Block`

````{py:attribute} configurable_fields
:canonical: agentsociety.cityagent.blocks.cognition_block.CognitionBlock.configurable_fields
:value: >
   ['top_k']

```{autodoc2-docstring} agentsociety.cityagent.blocks.cognition_block.CognitionBlock.configurable_fields
```

````

````{py:attribute} default_values
:canonical: agentsociety.cityagent.blocks.cognition_block.CognitionBlock.default_values
:value: >
   None

```{autodoc2-docstring} agentsociety.cityagent.blocks.cognition_block.CognitionBlock.default_values
```

````

````{py:attribute} fields_description
:canonical: agentsociety.cityagent.blocks.cognition_block.CognitionBlock.fields_description
:value: >
   None

```{autodoc2-docstring} agentsociety.cityagent.blocks.cognition_block.CognitionBlock.fields_description
```

````

````{py:method} set_status(status)
:canonical: agentsociety.cityagent.blocks.cognition_block.CognitionBlock.set_status
:async:

```{autodoc2-docstring} agentsociety.cityagent.blocks.cognition_block.CognitionBlock.set_status
```

````

````{py:method} attitude_update()
:canonical: agentsociety.cityagent.blocks.cognition_block.CognitionBlock.attitude_update
:async:

```{autodoc2-docstring} agentsociety.cityagent.blocks.cognition_block.CognitionBlock.attitude_update
```

````

````{py:method} thought_update()
:canonical: agentsociety.cityagent.blocks.cognition_block.CognitionBlock.thought_update
:async:

```{autodoc2-docstring} agentsociety.cityagent.blocks.cognition_block.CognitionBlock.thought_update
```

````

````{py:method} cross_day()
:canonical: agentsociety.cityagent.blocks.cognition_block.CognitionBlock.cross_day
:async:

```{autodoc2-docstring} agentsociety.cityagent.blocks.cognition_block.CognitionBlock.cross_day
```

````

````{py:method} forward()
:canonical: agentsociety.cityagent.blocks.cognition_block.CognitionBlock.forward
:async:

```{autodoc2-docstring} agentsociety.cityagent.blocks.cognition_block.CognitionBlock.forward
```

````

````{py:method} emotion_update(incident)
:canonical: agentsociety.cityagent.blocks.cognition_block.CognitionBlock.emotion_update
:async:

```{autodoc2-docstring} agentsociety.cityagent.blocks.cognition_block.CognitionBlock.emotion_update
```

````

`````
