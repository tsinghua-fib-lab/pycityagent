# {py:mod}`pycityagent.cityagent.firmagent`

```{py:module} pycityagent.cityagent.firmagent
```

```{autodoc2-docstring} pycityagent.cityagent.firmagent
:allowtitles:
```

## Module Contents

### Classes

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`FirmAgent <pycityagent.cityagent.firmagent.FirmAgent>`
  -
````

### Data

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`logger <pycityagent.cityagent.firmagent.logger>`
  - ```{autodoc2-docstring} pycityagent.cityagent.firmagent.logger
    :summary:
    ```
````

### API

````{py:data} logger
:canonical: pycityagent.cityagent.firmagent.logger
:value: >
   'getLogger(...)'

```{autodoc2-docstring} pycityagent.cityagent.firmagent.logger
```

````

`````{py:class} FirmAgent(name: str, llm_client: typing.Optional[pycityagent.llm.LLM] = None, simulator: typing.Optional[pycityagent.Simulator] = None, memory: typing.Optional[pycityagent.memory.Memory] = None, economy_client: typing.Optional[pycityagent.economy.EconomyClient] = None, messager: typing.Optional[pycityagent.message.Messager] = None, avro_file: typing.Optional[dict] = None)
:canonical: pycityagent.cityagent.firmagent.FirmAgent

Bases: {py:obj}`pycityagent.InstitutionAgent`

````{py:attribute} configurable_fields
:canonical: pycityagent.cityagent.firmagent.FirmAgent.configurable_fields
:value: >
   ['time_diff', 'max_price_inflation', 'max_wage_inflation']

```{autodoc2-docstring} pycityagent.cityagent.firmagent.FirmAgent.configurable_fields
```

````

````{py:attribute} default_values
:canonical: pycityagent.cityagent.firmagent.FirmAgent.default_values
:value: >
   None

```{autodoc2-docstring} pycityagent.cityagent.firmagent.FirmAgent.default_values
```

````

````{py:attribute} fields_description
:canonical: pycityagent.cityagent.firmagent.FirmAgent.fields_description
:value: >
   None

```{autodoc2-docstring} pycityagent.cityagent.firmagent.FirmAgent.fields_description
```

````

````{py:method} month_trigger()
:canonical: pycityagent.cityagent.firmagent.FirmAgent.month_trigger
:async:

```{autodoc2-docstring} pycityagent.cityagent.firmagent.FirmAgent.month_trigger
```

````

````{py:method} gather_messages(agent_ids, content)
:canonical: pycityagent.cityagent.firmagent.FirmAgent.gather_messages
:async:

````

````{py:method} forward()
:canonical: pycityagent.cityagent.firmagent.FirmAgent.forward
:async:

````

`````
