# {py:mod}`pycityagent.cityagent.societyagent`

```{py:module} pycityagent.cityagent.societyagent
```

```{autodoc2-docstring} pycityagent.cityagent.societyagent
:allowtitles:
```

## Module Contents

### Classes

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`PlanAndActionBlock <pycityagent.cityagent.societyagent.PlanAndActionBlock>`
  - ```{autodoc2-docstring} pycityagent.cityagent.societyagent.PlanAndActionBlock
    :summary:
    ```
* - {py:obj}`MindBlock <pycityagent.cityagent.societyagent.MindBlock>`
  - ```{autodoc2-docstring} pycityagent.cityagent.societyagent.MindBlock
    :summary:
    ```
* - {py:obj}`SocietyAgent <pycityagent.cityagent.societyagent.SocietyAgent>`
  -
````

### Data

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`logger <pycityagent.cityagent.societyagent.logger>`
  - ```{autodoc2-docstring} pycityagent.cityagent.societyagent.logger
    :summary:
    ```
````

### API

````{py:data} logger
:canonical: pycityagent.cityagent.societyagent.logger
:value: >
   'getLogger(...)'

```{autodoc2-docstring} pycityagent.cityagent.societyagent.logger
```

````

`````{py:class} PlanAndActionBlock(agent: pycityagent.agent.Agent, llm: pycityagent.llm.llm.LLM, memory: pycityagent.memory.Memory, simulator: pycityagent.Simulator, economy_client: pycityagent.economy.EconomyClient, enable_mobility: bool = True, enable_social: bool = True, enable_economy: bool = True, enable_cognition: bool = True)
:canonical: pycityagent.cityagent.societyagent.PlanAndActionBlock

Bases: {py:obj}`pycityagent.workflow.Block`

```{autodoc2-docstring} pycityagent.cityagent.societyagent.PlanAndActionBlock
```

```{rubric} Initialization
```

```{autodoc2-docstring} pycityagent.cityagent.societyagent.PlanAndActionBlock.__init__
```

````{py:attribute} longTermDecisionBlock
:canonical: pycityagent.cityagent.societyagent.PlanAndActionBlock.longTermDecisionBlock
:type: pycityagent.cityagent.blocks.economy_block.MonthPlanBlock
:value: >
   None

```{autodoc2-docstring} pycityagent.cityagent.societyagent.PlanAndActionBlock.longTermDecisionBlock
```

````

````{py:attribute} needsBlock
:canonical: pycityagent.cityagent.societyagent.PlanAndActionBlock.needsBlock
:type: pycityagent.cityagent.blocks.NeedsBlock
:value: >
   None

```{autodoc2-docstring} pycityagent.cityagent.societyagent.PlanAndActionBlock.needsBlock
```

````

````{py:attribute} planBlock
:canonical: pycityagent.cityagent.societyagent.PlanAndActionBlock.planBlock
:type: pycityagent.cityagent.blocks.PlanBlock
:value: >
   None

```{autodoc2-docstring} pycityagent.cityagent.societyagent.PlanAndActionBlock.planBlock
```

````

````{py:attribute} mobilityBlock
:canonical: pycityagent.cityagent.societyagent.PlanAndActionBlock.mobilityBlock
:type: pycityagent.cityagent.blocks.MobilityBlock
:value: >
   None

```{autodoc2-docstring} pycityagent.cityagent.societyagent.PlanAndActionBlock.mobilityBlock
```

````

````{py:attribute} socialBlock
:canonical: pycityagent.cityagent.societyagent.PlanAndActionBlock.socialBlock
:type: pycityagent.cityagent.blocks.SocialBlock
:value: >
   None

```{autodoc2-docstring} pycityagent.cityagent.societyagent.PlanAndActionBlock.socialBlock
```

````

````{py:attribute} economyBlock
:canonical: pycityagent.cityagent.societyagent.PlanAndActionBlock.economyBlock
:type: pycityagent.cityagent.blocks.EconomyBlock
:value: >
   None

```{autodoc2-docstring} pycityagent.cityagent.societyagent.PlanAndActionBlock.economyBlock
```

````

````{py:attribute} otherBlock
:canonical: pycityagent.cityagent.societyagent.PlanAndActionBlock.otherBlock
:type: pycityagent.cityagent.blocks.OtherBlock
:value: >
   None

```{autodoc2-docstring} pycityagent.cityagent.societyagent.PlanAndActionBlock.otherBlock
```

````

````{py:method} plan_generation()
:canonical: pycityagent.cityagent.societyagent.PlanAndActionBlock.plan_generation
:async:

```{autodoc2-docstring} pycityagent.cityagent.societyagent.PlanAndActionBlock.plan_generation
```

````

````{py:method} step_execution()
:canonical: pycityagent.cityagent.societyagent.PlanAndActionBlock.step_execution
:async:

```{autodoc2-docstring} pycityagent.cityagent.societyagent.PlanAndActionBlock.step_execution
```

````

````{py:method} forward()
:canonical: pycityagent.cityagent.societyagent.PlanAndActionBlock.forward
:async:

````

`````

`````{py:class} MindBlock(llm: pycityagent.llm.llm.LLM, memory: pycityagent.memory.Memory, simulator: pycityagent.Simulator)
:canonical: pycityagent.cityagent.societyagent.MindBlock

Bases: {py:obj}`pycityagent.workflow.Block`

```{autodoc2-docstring} pycityagent.cityagent.societyagent.MindBlock
```

```{rubric} Initialization
```

```{autodoc2-docstring} pycityagent.cityagent.societyagent.MindBlock.__init__
```

````{py:attribute} cognitionBlock
:canonical: pycityagent.cityagent.societyagent.MindBlock.cognitionBlock
:type: pycityagent.cityagent.blocks.CognitionBlock
:value: >
   None

```{autodoc2-docstring} pycityagent.cityagent.societyagent.MindBlock.cognitionBlock
```

````

````{py:method} forward()
:canonical: pycityagent.cityagent.societyagent.MindBlock.forward
:async:

````

`````

`````{py:class} SocietyAgent(name: str, llm_client: typing.Optional[pycityagent.llm.llm.LLM] = None, simulator: typing.Optional[pycityagent.Simulator] = None, memory: typing.Optional[pycityagent.memory.Memory] = None, economy_client: typing.Optional[pycityagent.economy.EconomyClient] = None)
:canonical: pycityagent.cityagent.societyagent.SocietyAgent

Bases: {py:obj}`pycityagent.CitizenAgent`

````{py:attribute} update_with_sim
:canonical: pycityagent.cityagent.societyagent.SocietyAgent.update_with_sim
:value: >
   'UpdateWithSimulator(...)'

```{autodoc2-docstring} pycityagent.cityagent.societyagent.SocietyAgent.update_with_sim
```

````

````{py:attribute} mindBlock
:canonical: pycityagent.cityagent.societyagent.SocietyAgent.mindBlock
:type: pycityagent.cityagent.societyagent.MindBlock
:value: >
   None

```{autodoc2-docstring} pycityagent.cityagent.societyagent.SocietyAgent.mindBlock
```

````

````{py:attribute} planAndActionBlock
:canonical: pycityagent.cityagent.societyagent.SocietyAgent.planAndActionBlock
:type: pycityagent.cityagent.societyagent.PlanAndActionBlock
:value: >
   None

```{autodoc2-docstring} pycityagent.cityagent.societyagent.SocietyAgent.planAndActionBlock
```

````

````{py:attribute} configurable_fields
:canonical: pycityagent.cityagent.societyagent.SocietyAgent.configurable_fields
:value: >
   ['enable_cognition', 'enable_mobility', 'enable_social', 'enable_economy']

```{autodoc2-docstring} pycityagent.cityagent.societyagent.SocietyAgent.configurable_fields
```

````

````{py:attribute} default_values
:canonical: pycityagent.cityagent.societyagent.SocietyAgent.default_values
:value: >
   None

```{autodoc2-docstring} pycityagent.cityagent.societyagent.SocietyAgent.default_values
```

````

````{py:attribute} fields_description
:canonical: pycityagent.cityagent.societyagent.SocietyAgent.fields_description
:value: >
   None

```{autodoc2-docstring} pycityagent.cityagent.societyagent.SocietyAgent.fields_description
```

````

````{py:method} forward()
:canonical: pycityagent.cityagent.societyagent.SocietyAgent.forward
:async:

````

````{py:method} check_and_update_step()
:canonical: pycityagent.cityagent.societyagent.SocietyAgent.check_and_update_step
:async:

```{autodoc2-docstring} pycityagent.cityagent.societyagent.SocietyAgent.check_and_update_step
```

````

````{py:method} process_agent_chat_response(payload: dict) -> str
:canonical: pycityagent.cityagent.societyagent.SocietyAgent.process_agent_chat_response
:async:

````

`````
