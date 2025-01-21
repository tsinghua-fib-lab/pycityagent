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

`````{py:class} BankAgent(name: str, llm_client: typing.Optional[pycityagent.llm.llm.LLM] = None, simulator: typing.Optional[pycityagent.Simulator] = None, memory: typing.Optional[pycityagent.memory.Memory] = None, economy_client: typing.Optional[pycityagent.economy.EconomyClient] = None, messager: typing.Optional[pycityagent.message.Messager] = None, avro_file: typing.Optional[dict] = None)
:canonical: pycityagent.cityagent.bankagent.BankAgent

Bases: {py:obj}`pycityagent.InstitutionAgent`

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
