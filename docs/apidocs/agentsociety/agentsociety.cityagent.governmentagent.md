# {py:mod}`agentsociety.cityagent.governmentagent`

```{py:module} agentsociety.cityagent.governmentagent
```

```{autodoc2-docstring} agentsociety.cityagent.governmentagent
:allowtitles:
```

## Module Contents

### Classes

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`GovernmentAgent <agentsociety.cityagent.governmentagent.GovernmentAgent>`
  -
````

### Data

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`logger <agentsociety.cityagent.governmentagent.logger>`
  - ```{autodoc2-docstring} agentsociety.cityagent.governmentagent.logger
    :summary:
    ```
````

### API

````{py:data} logger
:canonical: agentsociety.cityagent.governmentagent.logger
:value: >
   'getLogger(...)'

```{autodoc2-docstring} agentsociety.cityagent.governmentagent.logger
```

````

`````{py:class} GovernmentAgent(name: str, llm_client: typing.Optional[agentsociety.llm.llm.LLM] = None, simulator: typing.Optional[agentsociety.Simulator] = None, memory: typing.Optional[agentsociety.memory.Memory] = None, economy_client: typing.Optional[agentsociety.environment.EconomyClient] = None, messager: typing.Optional[agentsociety.message.Messager] = None, avro_file: typing.Optional[dict] = None)
:canonical: agentsociety.cityagent.governmentagent.GovernmentAgent

Bases: {py:obj}`agentsociety.InstitutionAgent`

````{py:attribute} configurable_fields
:canonical: agentsociety.cityagent.governmentagent.GovernmentAgent.configurable_fields
:value: >
   ['time_diff']

```{autodoc2-docstring} agentsociety.cityagent.governmentagent.GovernmentAgent.configurable_fields
```

````

````{py:attribute} default_values
:canonical: agentsociety.cityagent.governmentagent.GovernmentAgent.default_values
:value: >
   None

```{autodoc2-docstring} agentsociety.cityagent.governmentagent.GovernmentAgent.default_values
```

````

````{py:attribute} fields_description
:canonical: agentsociety.cityagent.governmentagent.GovernmentAgent.fields_description
:value: >
   None

```{autodoc2-docstring} agentsociety.cityagent.governmentagent.GovernmentAgent.fields_description
```

````

````{py:method} month_trigger()
:canonical: agentsociety.cityagent.governmentagent.GovernmentAgent.month_trigger
:async:

```{autodoc2-docstring} agentsociety.cityagent.governmentagent.GovernmentAgent.month_trigger
```

````

````{py:method} gather_messages(agent_ids, content)
:canonical: agentsociety.cityagent.governmentagent.GovernmentAgent.gather_messages
:async:

````

````{py:method} forward()
:canonical: agentsociety.cityagent.governmentagent.GovernmentAgent.forward
:async:

````

`````
