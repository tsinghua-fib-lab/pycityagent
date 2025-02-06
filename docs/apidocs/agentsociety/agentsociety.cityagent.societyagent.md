# {py:mod}`agentsociety.cityagent.societyagent`

```{py:module} agentsociety.cityagent.societyagent
```

```{autodoc2-docstring} agentsociety.cityagent.societyagent
:allowtitles:
```

## Module Contents

### Classes

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`PlanAndActionBlock <agentsociety.cityagent.societyagent.PlanAndActionBlock>`
  - ```{autodoc2-docstring} agentsociety.cityagent.societyagent.PlanAndActionBlock
    :summary:
    ```
* - {py:obj}`MindBlock <agentsociety.cityagent.societyagent.MindBlock>`
  - ```{autodoc2-docstring} agentsociety.cityagent.societyagent.MindBlock
    :summary:
    ```
* - {py:obj}`SocietyAgent <agentsociety.cityagent.societyagent.SocietyAgent>`
  -
````

### Data

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`logger <agentsociety.cityagent.societyagent.logger>`
  - ```{autodoc2-docstring} agentsociety.cityagent.societyagent.logger
    :summary:
    ```
````

### API

````{py:data} logger
:canonical: agentsociety.cityagent.societyagent.logger
:value: >
   'getLogger(...)'

```{autodoc2-docstring} agentsociety.cityagent.societyagent.logger
```

````

`````{py:class} PlanAndActionBlock(agent: agentsociety.agent.Agent, llm: agentsociety.llm.llm.LLM, memory: agentsociety.memory.Memory, simulator: agentsociety.Simulator, economy_client: agentsociety.environment.EconomyClient, enable_mobility: bool = True, enable_social: bool = True, enable_economy: bool = True, enable_cognition: bool = True)
:canonical: agentsociety.cityagent.societyagent.PlanAndActionBlock

Bases: {py:obj}`agentsociety.workflow.Block`

```{autodoc2-docstring} agentsociety.cityagent.societyagent.PlanAndActionBlock
```

```{rubric} Initialization
```

```{autodoc2-docstring} agentsociety.cityagent.societyagent.PlanAndActionBlock.__init__
```

````{py:attribute} monthPlanBlock
:canonical: agentsociety.cityagent.societyagent.PlanAndActionBlock.monthPlanBlock
:type: agentsociety.cityagent.blocks.economy_block.MonthPlanBlock
:value: >
   None

```{autodoc2-docstring} agentsociety.cityagent.societyagent.PlanAndActionBlock.monthPlanBlock
```

````

````{py:attribute} needsBlock
:canonical: agentsociety.cityagent.societyagent.PlanAndActionBlock.needsBlock
:type: agentsociety.cityagent.blocks.NeedsBlock
:value: >
   None

```{autodoc2-docstring} agentsociety.cityagent.societyagent.PlanAndActionBlock.needsBlock
```

````

````{py:attribute} planBlock
:canonical: agentsociety.cityagent.societyagent.PlanAndActionBlock.planBlock
:type: agentsociety.cityagent.blocks.PlanBlock
:value: >
   None

```{autodoc2-docstring} agentsociety.cityagent.societyagent.PlanAndActionBlock.planBlock
```

````

````{py:attribute} mobilityBlock
:canonical: agentsociety.cityagent.societyagent.PlanAndActionBlock.mobilityBlock
:type: agentsociety.cityagent.blocks.MobilityBlock
:value: >
   None

```{autodoc2-docstring} agentsociety.cityagent.societyagent.PlanAndActionBlock.mobilityBlock
```

````

````{py:attribute} socialBlock
:canonical: agentsociety.cityagent.societyagent.PlanAndActionBlock.socialBlock
:type: agentsociety.cityagent.blocks.SocialBlock
:value: >
   None

```{autodoc2-docstring} agentsociety.cityagent.societyagent.PlanAndActionBlock.socialBlock
```

````

````{py:attribute} economyBlock
:canonical: agentsociety.cityagent.societyagent.PlanAndActionBlock.economyBlock
:type: agentsociety.cityagent.blocks.EconomyBlock
:value: >
   None

```{autodoc2-docstring} agentsociety.cityagent.societyagent.PlanAndActionBlock.economyBlock
```

````

````{py:attribute} otherBlock
:canonical: agentsociety.cityagent.societyagent.PlanAndActionBlock.otherBlock
:type: agentsociety.cityagent.blocks.OtherBlock
:value: >
   None

```{autodoc2-docstring} agentsociety.cityagent.societyagent.PlanAndActionBlock.otherBlock
```

````

````{py:method} plan_generation()
:canonical: agentsociety.cityagent.societyagent.PlanAndActionBlock.plan_generation
:async:

```{autodoc2-docstring} agentsociety.cityagent.societyagent.PlanAndActionBlock.plan_generation
```

````

````{py:method} step_execution()
:canonical: agentsociety.cityagent.societyagent.PlanAndActionBlock.step_execution
:async:

```{autodoc2-docstring} agentsociety.cityagent.societyagent.PlanAndActionBlock.step_execution
```

````

````{py:method} forward()
:canonical: agentsociety.cityagent.societyagent.PlanAndActionBlock.forward
:async:

````

`````

`````{py:class} MindBlock(llm: agentsociety.llm.llm.LLM, memory: agentsociety.memory.Memory, simulator: agentsociety.Simulator)
:canonical: agentsociety.cityagent.societyagent.MindBlock

Bases: {py:obj}`agentsociety.workflow.Block`

```{autodoc2-docstring} agentsociety.cityagent.societyagent.MindBlock
```

```{rubric} Initialization
```

```{autodoc2-docstring} agentsociety.cityagent.societyagent.MindBlock.__init__
```

````{py:attribute} cognitionBlock
:canonical: agentsociety.cityagent.societyagent.MindBlock.cognitionBlock
:type: agentsociety.cityagent.blocks.CognitionBlock
:value: >
   None

```{autodoc2-docstring} agentsociety.cityagent.societyagent.MindBlock.cognitionBlock
```

````

````{py:method} forward()
:canonical: agentsociety.cityagent.societyagent.MindBlock.forward
:async:

````

`````

`````{py:class} SocietyAgent(name: str, llm_client: typing.Optional[agentsociety.llm.llm.LLM] = None, simulator: typing.Optional[agentsociety.Simulator] = None, memory: typing.Optional[agentsociety.memory.Memory] = None, economy_client: typing.Optional[agentsociety.environment.EconomyClient] = None)
:canonical: agentsociety.cityagent.societyagent.SocietyAgent

Bases: {py:obj}`agentsociety.CitizenAgent`

````{py:attribute} update_with_sim
:canonical: agentsociety.cityagent.societyagent.SocietyAgent.update_with_sim
:value: >
   'UpdateWithSimulator(...)'

```{autodoc2-docstring} agentsociety.cityagent.societyagent.SocietyAgent.update_with_sim
```

````

````{py:attribute} mindBlock
:canonical: agentsociety.cityagent.societyagent.SocietyAgent.mindBlock
:type: agentsociety.cityagent.societyagent.MindBlock
:value: >
   None

```{autodoc2-docstring} agentsociety.cityagent.societyagent.SocietyAgent.mindBlock
```

````

````{py:attribute} planAndActionBlock
:canonical: agentsociety.cityagent.societyagent.SocietyAgent.planAndActionBlock
:type: agentsociety.cityagent.societyagent.PlanAndActionBlock
:value: >
   None

```{autodoc2-docstring} agentsociety.cityagent.societyagent.SocietyAgent.planAndActionBlock
```

````

````{py:attribute} configurable_fields
:canonical: agentsociety.cityagent.societyagent.SocietyAgent.configurable_fields
:value: >
   ['enable_cognition', 'enable_mobility', 'enable_social', 'enable_economy']

```{autodoc2-docstring} agentsociety.cityagent.societyagent.SocietyAgent.configurable_fields
```

````

````{py:attribute} default_values
:canonical: agentsociety.cityagent.societyagent.SocietyAgent.default_values
:value: >
   None

```{autodoc2-docstring} agentsociety.cityagent.societyagent.SocietyAgent.default_values
```

````

````{py:attribute} fields_description
:canonical: agentsociety.cityagent.societyagent.SocietyAgent.fields_description
:value: >
   None

```{autodoc2-docstring} agentsociety.cityagent.societyagent.SocietyAgent.fields_description
```

````

````{py:method} forward()
:canonical: agentsociety.cityagent.societyagent.SocietyAgent.forward
:async:

````

````{py:method} check_and_update_step()
:canonical: agentsociety.cityagent.societyagent.SocietyAgent.check_and_update_step
:async:

```{autodoc2-docstring} agentsociety.cityagent.societyagent.SocietyAgent.check_and_update_step
```

````

````{py:method} process_agent_chat_response(payload: dict) -> str
:canonical: agentsociety.cityagent.societyagent.SocietyAgent.process_agent_chat_response
:async:

````

`````
