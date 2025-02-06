# {py:mod}`agentsociety.cityagent.nbsagent`

```{py:module} agentsociety.cityagent.nbsagent
```

```{autodoc2-docstring} agentsociety.cityagent.nbsagent
:allowtitles:
```

## Module Contents

### Classes

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`NBSAgent <agentsociety.cityagent.nbsagent.NBSAgent>`
  -
````

### Data

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`logger <agentsociety.cityagent.nbsagent.logger>`
  - ```{autodoc2-docstring} agentsociety.cityagent.nbsagent.logger
    :summary:
    ```
````

### API

````{py:data} logger
:canonical: agentsociety.cityagent.nbsagent.logger
:value: >
   'getLogger(...)'

```{autodoc2-docstring} agentsociety.cityagent.nbsagent.logger
```

````

`````{py:class} NBSAgent(name: str, llm_client: typing.Optional[agentsociety.llm.llm.LLM] = None, simulator: typing.Optional[agentsociety.Simulator] = None, memory: typing.Optional[agentsociety.memory.Memory] = None, economy_client: typing.Optional[agentsociety.environment.EconomyClient] = None, messager: typing.Optional[agentsociety.message.Messager] = None, avro_file: typing.Optional[dict] = None)
:canonical: agentsociety.cityagent.nbsagent.NBSAgent

Bases: {py:obj}`agentsociety.InstitutionAgent`

````{py:attribute} configurable_fields
:canonical: agentsociety.cityagent.nbsagent.NBSAgent.configurable_fields
:value: >
   ['time_diff', 'num_labor_hours', 'productivity_per_labor']

```{autodoc2-docstring} agentsociety.cityagent.nbsagent.NBSAgent.configurable_fields
```

````

````{py:attribute} default_values
:canonical: agentsociety.cityagent.nbsagent.NBSAgent.default_values
:value: >
   None

```{autodoc2-docstring} agentsociety.cityagent.nbsagent.NBSAgent.default_values
```

````

````{py:attribute} fields_description
:canonical: agentsociety.cityagent.nbsagent.NBSAgent.fields_description
:value: >
   None

```{autodoc2-docstring} agentsociety.cityagent.nbsagent.NBSAgent.fields_description
```

````

````{py:method} month_trigger()
:canonical: agentsociety.cityagent.nbsagent.NBSAgent.month_trigger
:async:

```{autodoc2-docstring} agentsociety.cityagent.nbsagent.NBSAgent.month_trigger
```

````

````{py:method} gather_messages(agent_ids, content)
:canonical: agentsociety.cityagent.nbsagent.NBSAgent.gather_messages
:async:

````

````{py:method} forward()
:canonical: agentsociety.cityagent.nbsagent.NBSAgent.forward
:async:

````

`````
