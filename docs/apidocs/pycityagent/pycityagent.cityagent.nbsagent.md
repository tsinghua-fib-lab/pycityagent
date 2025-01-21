# {py:mod}`pycityagent.cityagent.nbsagent`

```{py:module} pycityagent.cityagent.nbsagent
```

```{autodoc2-docstring} pycityagent.cityagent.nbsagent
:allowtitles:
```

## Module Contents

### Classes

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`NBSAgent <pycityagent.cityagent.nbsagent.NBSAgent>`
  -
````

### Data

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`logger <pycityagent.cityagent.nbsagent.logger>`
  - ```{autodoc2-docstring} pycityagent.cityagent.nbsagent.logger
    :summary:
    ```
````

### API

````{py:data} logger
:canonical: pycityagent.cityagent.nbsagent.logger
:value: >
   'getLogger(...)'

```{autodoc2-docstring} pycityagent.cityagent.nbsagent.logger
```

````

`````{py:class} NBSAgent(name: str, llm_client: typing.Optional[pycityagent.llm.llm.LLM] = None, simulator: typing.Optional[pycityagent.Simulator] = None, memory: typing.Optional[pycityagent.memory.Memory] = None, economy_client: typing.Optional[pycityagent.economy.EconomyClient] = None, messager: typing.Optional[pycityagent.message.Messager] = None, avro_file: typing.Optional[dict] = None)
:canonical: pycityagent.cityagent.nbsagent.NBSAgent

Bases: {py:obj}`pycityagent.InstitutionAgent`

````{py:method} month_trigger()
:canonical: pycityagent.cityagent.nbsagent.NBSAgent.month_trigger
:async:

```{autodoc2-docstring} pycityagent.cityagent.nbsagent.NBSAgent.month_trigger
```

````

````{py:method} gather_messages(agent_ids, content)
:canonical: pycityagent.cityagent.nbsagent.NBSAgent.gather_messages
:async:

````

````{py:method} forward()
:canonical: pycityagent.cityagent.nbsagent.NBSAgent.forward
:async:

````

`````
