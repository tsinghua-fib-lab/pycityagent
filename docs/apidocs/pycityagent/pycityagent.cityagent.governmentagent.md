# {py:mod}`pycityagent.cityagent.governmentagent`

```{py:module} pycityagent.cityagent.governmentagent
```

```{autodoc2-docstring} pycityagent.cityagent.governmentagent
:allowtitles:
```

## Module Contents

### Classes

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`GovernmentAgent <pycityagent.cityagent.governmentagent.GovernmentAgent>`
  -
````

### Data

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`logger <pycityagent.cityagent.governmentagent.logger>`
  - ```{autodoc2-docstring} pycityagent.cityagent.governmentagent.logger
    :summary:
    ```
````

### API

````{py:data} logger
:canonical: pycityagent.cityagent.governmentagent.logger
:value: >
   'getLogger(...)'

```{autodoc2-docstring} pycityagent.cityagent.governmentagent.logger
```

````

`````{py:class} GovernmentAgent(name: str, llm_client: typing.Optional[pycityagent.llm.llm.LLM] = None, simulator: typing.Optional[pycityagent.Simulator] = None, memory: typing.Optional[pycityagent.memory.Memory] = None, economy_client: typing.Optional[pycityagent.economy.EconomyClient] = None, messager: typing.Optional[pycityagent.message.Messager] = None, avro_file: typing.Optional[dict] = None)
:canonical: pycityagent.cityagent.governmentagent.GovernmentAgent

Bases: {py:obj}`pycityagent.InstitutionAgent`

````{py:method} month_trigger()
:canonical: pycityagent.cityagent.governmentagent.GovernmentAgent.month_trigger
:async:

```{autodoc2-docstring} pycityagent.cityagent.governmentagent.GovernmentAgent.month_trigger
```

````

````{py:method} gather_messages(agent_ids, content)
:canonical: pycityagent.cityagent.governmentagent.GovernmentAgent.gather_messages
:async:

````

````{py:method} forward()
:canonical: pycityagent.cityagent.governmentagent.GovernmentAgent.forward
:async:

````

`````
