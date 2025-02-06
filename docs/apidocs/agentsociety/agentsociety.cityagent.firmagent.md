# {py:mod}`agentsociety.cityagent.firmagent`

```{py:module} agentsociety.cityagent.firmagent
```

```{autodoc2-docstring} agentsociety.cityagent.firmagent
:allowtitles:
```

## Module Contents

### Classes

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`FirmAgent <agentsociety.cityagent.firmagent.FirmAgent>`
  -
````

### Data

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`logger <agentsociety.cityagent.firmagent.logger>`
  - ```{autodoc2-docstring} agentsociety.cityagent.firmagent.logger
    :summary:
    ```
````

### API

````{py:data} logger
:canonical: agentsociety.cityagent.firmagent.logger
:value: >
   'getLogger(...)'

```{autodoc2-docstring} agentsociety.cityagent.firmagent.logger
```

````

`````{py:class} FirmAgent(name: str, llm_client: typing.Optional[agentsociety.llm.LLM] = None, simulator: typing.Optional[agentsociety.Simulator] = None, memory: typing.Optional[agentsociety.memory.Memory] = None, economy_client: typing.Optional[agentsociety.environment.EconomyClient] = None, messager: typing.Optional[agentsociety.message.Messager] = None, avro_file: typing.Optional[dict] = None)
:canonical: agentsociety.cityagent.firmagent.FirmAgent

Bases: {py:obj}`agentsociety.InstitutionAgent`

````{py:attribute} configurable_fields
:canonical: agentsociety.cityagent.firmagent.FirmAgent.configurable_fields
:value: >
   ['time_diff', 'max_price_inflation', 'max_wage_inflation']

```{autodoc2-docstring} agentsociety.cityagent.firmagent.FirmAgent.configurable_fields
```

````

````{py:attribute} default_values
:canonical: agentsociety.cityagent.firmagent.FirmAgent.default_values
:value: >
   None

```{autodoc2-docstring} agentsociety.cityagent.firmagent.FirmAgent.default_values
```

````

````{py:attribute} fields_description
:canonical: agentsociety.cityagent.firmagent.FirmAgent.fields_description
:value: >
   None

```{autodoc2-docstring} agentsociety.cityagent.firmagent.FirmAgent.fields_description
```

````

````{py:method} month_trigger()
:canonical: agentsociety.cityagent.firmagent.FirmAgent.month_trigger
:async:

```{autodoc2-docstring} agentsociety.cityagent.firmagent.FirmAgent.month_trigger
```

````

````{py:method} gather_messages(agent_ids, content)
:canonical: agentsociety.cityagent.firmagent.FirmAgent.gather_messages
:async:

````

````{py:method} forward()
:canonical: agentsociety.cityagent.firmagent.FirmAgent.forward
:async:

````

`````
