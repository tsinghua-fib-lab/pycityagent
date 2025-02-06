# {py:mod}`agentsociety.cityagent.bankagent`

```{py:module} agentsociety.cityagent.bankagent
```

```{autodoc2-docstring} agentsociety.cityagent.bankagent
:allowtitles:
```

## Module Contents

### Classes

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`BankAgent <agentsociety.cityagent.bankagent.BankAgent>`
  -
````

### Functions

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`calculate_inflation <agentsociety.cityagent.bankagent.calculate_inflation>`
  - ```{autodoc2-docstring} agentsociety.cityagent.bankagent.calculate_inflation
    :summary:
    ```
````

### Data

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`logger <agentsociety.cityagent.bankagent.logger>`
  - ```{autodoc2-docstring} agentsociety.cityagent.bankagent.logger
    :summary:
    ```
````

### API

````{py:data} logger
:canonical: agentsociety.cityagent.bankagent.logger
:value: >
   'getLogger(...)'

```{autodoc2-docstring} agentsociety.cityagent.bankagent.logger
```

````

````{py:function} calculate_inflation(prices)
:canonical: agentsociety.cityagent.bankagent.calculate_inflation

```{autodoc2-docstring} agentsociety.cityagent.bankagent.calculate_inflation
```
````

`````{py:class} BankAgent(name: str, llm_client: typing.Optional[agentsociety.llm.llm.LLM] = None, simulator: typing.Optional[agentsociety.Simulator] = None, memory: typing.Optional[agentsociety.memory.Memory] = None, economy_client: typing.Optional[agentsociety.environment.EconomyClient] = None, messager: typing.Optional[agentsociety.message.Messager] = None, avro_file: typing.Optional[dict] = None)
:canonical: agentsociety.cityagent.bankagent.BankAgent

Bases: {py:obj}`agentsociety.InstitutionAgent`

````{py:attribute} configurable_fields
:canonical: agentsociety.cityagent.bankagent.BankAgent.configurable_fields
:value: >
   ['time_diff']

```{autodoc2-docstring} agentsociety.cityagent.bankagent.BankAgent.configurable_fields
```

````

````{py:attribute} default_values
:canonical: agentsociety.cityagent.bankagent.BankAgent.default_values
:value: >
   None

```{autodoc2-docstring} agentsociety.cityagent.bankagent.BankAgent.default_values
```

````

````{py:attribute} fields_description
:canonical: agentsociety.cityagent.bankagent.BankAgent.fields_description
:value: >
   None

```{autodoc2-docstring} agentsociety.cityagent.bankagent.BankAgent.fields_description
```

````

````{py:method} month_trigger()
:canonical: agentsociety.cityagent.bankagent.BankAgent.month_trigger
:async:

```{autodoc2-docstring} agentsociety.cityagent.bankagent.BankAgent.month_trigger
```

````

````{py:method} gather_messages(agent_ids, content)
:canonical: agentsociety.cityagent.bankagent.BankAgent.gather_messages
:async:

````

````{py:method} forward()
:canonical: agentsociety.cityagent.bankagent.BankAgent.forward
:async:

````

`````
