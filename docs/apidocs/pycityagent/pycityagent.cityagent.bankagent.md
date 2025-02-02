# {py:mod}`pycityagent.cityagent.bankagent`

```{py:module} pycityagent.cityagent.bankagent
```

```{autodoc2-docstring} pycityagent.cityagent.bankagent
:allowtitles:
```

## Module Contents

### Classes

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`BankAgent <pycityagent.cityagent.bankagent.BankAgent>`
  -
````

### Functions

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`calculate_inflation <pycityagent.cityagent.bankagent.calculate_inflation>`
  - ```{autodoc2-docstring} pycityagent.cityagent.bankagent.calculate_inflation
    :summary:
    ```
````

### Data

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`logger <pycityagent.cityagent.bankagent.logger>`
  - ```{autodoc2-docstring} pycityagent.cityagent.bankagent.logger
    :summary:
    ```
````

### API

````{py:data} logger
:canonical: pycityagent.cityagent.bankagent.logger
:value: >
   'getLogger(...)'

```{autodoc2-docstring} pycityagent.cityagent.bankagent.logger
```

````

````{py:function} calculate_inflation(prices)
:canonical: pycityagent.cityagent.bankagent.calculate_inflation

```{autodoc2-docstring} pycityagent.cityagent.bankagent.calculate_inflation
```
````

`````{py:class} BankAgent(name: str, llm_client: typing.Optional[pycityagent.llm.llm.LLM] = None, simulator: typing.Optional[pycityagent.Simulator] = None, memory: typing.Optional[pycityagent.memory.Memory] = None, economy_client: typing.Optional[pycityagent.environment.EconomyClient] = None, messager: typing.Optional[pycityagent.message.Messager] = None, avro_file: typing.Optional[dict] = None)
:canonical: pycityagent.cityagent.bankagent.BankAgent

Bases: {py:obj}`pycityagent.InstitutionAgent`

````{py:attribute} configurable_fields
:canonical: pycityagent.cityagent.bankagent.BankAgent.configurable_fields
:value: >
   ['time_diff']

```{autodoc2-docstring} pycityagent.cityagent.bankagent.BankAgent.configurable_fields
```

````

````{py:attribute} default_values
:canonical: pycityagent.cityagent.bankagent.BankAgent.default_values
:value: >
   None

```{autodoc2-docstring} pycityagent.cityagent.bankagent.BankAgent.default_values
```

````

````{py:attribute} fields_description
:canonical: pycityagent.cityagent.bankagent.BankAgent.fields_description
:value: >
   None

```{autodoc2-docstring} pycityagent.cityagent.bankagent.BankAgent.fields_description
```

````

````{py:method} month_trigger()
:canonical: pycityagent.cityagent.bankagent.BankAgent.month_trigger
:async:

```{autodoc2-docstring} pycityagent.cityagent.bankagent.BankAgent.month_trigger
```

````

````{py:method} gather_messages(agent_ids, content)
:canonical: pycityagent.cityagent.bankagent.BankAgent.gather_messages
:async:

````

````{py:method} forward()
:canonical: pycityagent.cityagent.bankagent.BankAgent.forward
:async:

````

`````
