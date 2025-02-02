# {py:mod}`pycityagent.agent.agent`

```{py:module} pycityagent.agent.agent
```

```{autodoc2-docstring} pycityagent.agent.agent
:allowtitles:
```

## Module Contents

### Classes

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`CitizenAgent <pycityagent.agent.agent.CitizenAgent>`
  - ```{autodoc2-docstring} pycityagent.agent.agent.CitizenAgent
    :summary:
    ```
* - {py:obj}`InstitutionAgent <pycityagent.agent.agent.InstitutionAgent>`
  - ```{autodoc2-docstring} pycityagent.agent.agent.InstitutionAgent
    :summary:
    ```
````

### Data

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`logger <pycityagent.agent.agent.logger>`
  - ```{autodoc2-docstring} pycityagent.agent.agent.logger
    :summary:
    ```
* - {py:obj}`__all__ <pycityagent.agent.agent.__all__>`
  - ```{autodoc2-docstring} pycityagent.agent.agent.__all__
    :summary:
    ```
````

### API

````{py:data} logger
:canonical: pycityagent.agent.agent.logger
:value: >
   'getLogger(...)'

```{autodoc2-docstring} pycityagent.agent.agent.logger
```

````

````{py:data} __all__
:canonical: pycityagent.agent.agent.__all__
:value: >
   ['InstitutionAgent', 'CitizenAgent']

```{autodoc2-docstring} pycityagent.agent.agent.__all__
```

````

`````{py:class} CitizenAgent(name: str, llm_client: typing.Optional[pycityagent.llm.LLM] = None, simulator: typing.Optional[pycityagent.environment.Simulator] = None, memory: typing.Optional[pycityagent.memory.Memory] = None, economy_client: typing.Optional[pycityagent.environment.EconomyClient] = None, messager: typing.Optional[pycityagent.message.Messager] = None, message_interceptor: typing.Optional[pycityagent.message.MessageInterceptor] = None, avro_file: typing.Optional[dict] = None)
:canonical: pycityagent.agent.agent.CitizenAgent

Bases: {py:obj}`pycityagent.agent.agent_base.Agent`

```{autodoc2-docstring} pycityagent.agent.agent.CitizenAgent
```

```{rubric} Initialization
```

```{autodoc2-docstring} pycityagent.agent.agent.CitizenAgent.__init__
```

````{py:method} bind_to_simulator()
:canonical: pycityagent.agent.agent.CitizenAgent.bind_to_simulator
:async:

```{autodoc2-docstring} pycityagent.agent.agent.CitizenAgent.bind_to_simulator
```

````

````{py:method} _bind_to_simulator()
:canonical: pycityagent.agent.agent.CitizenAgent._bind_to_simulator
:async:

```{autodoc2-docstring} pycityagent.agent.agent.CitizenAgent._bind_to_simulator
```

````

````{py:method} _bind_to_economy()
:canonical: pycityagent.agent.agent.CitizenAgent._bind_to_economy
:async:

```{autodoc2-docstring} pycityagent.agent.agent.CitizenAgent._bind_to_economy
```

````

````{py:method} handle_gather_message(payload: dict)
:canonical: pycityagent.agent.agent.CitizenAgent.handle_gather_message
:async:

```{autodoc2-docstring} pycityagent.agent.agent.CitizenAgent.handle_gather_message
```

````

````{py:property} mlflow_client
:canonical: pycityagent.agent.agent.CitizenAgent.mlflow_client
:type: pycityagent.metrics.MlflowClient

```{autodoc2-docstring} pycityagent.agent.agent.CitizenAgent.mlflow_client
```

````

````{py:method} set_mlflow_client(mlflow_client: pycityagent.metrics.MlflowClient)
:canonical: pycityagent.agent.agent.CitizenAgent.set_mlflow_client

```{autodoc2-docstring} pycityagent.agent.agent.CitizenAgent.set_mlflow_client
```

````

`````

`````{py:class} InstitutionAgent(name: str, llm_client: typing.Optional[pycityagent.llm.LLM] = None, simulator: typing.Optional[pycityagent.environment.Simulator] = None, memory: typing.Optional[pycityagent.memory.Memory] = None, economy_client: typing.Optional[pycityagent.environment.EconomyClient] = None, messager: typing.Optional[pycityagent.message.Messager] = None, message_interceptor: typing.Optional[pycityagent.message.MessageInterceptor] = None, avro_file: typing.Optional[dict] = None)
:canonical: pycityagent.agent.agent.InstitutionAgent

Bases: {py:obj}`pycityagent.agent.agent_base.Agent`

```{autodoc2-docstring} pycityagent.agent.agent.InstitutionAgent
```

```{rubric} Initialization
```

```{autodoc2-docstring} pycityagent.agent.agent.InstitutionAgent.__init__
```

````{py:method} bind_to_simulator()
:canonical: pycityagent.agent.agent.InstitutionAgent.bind_to_simulator
:async:

```{autodoc2-docstring} pycityagent.agent.agent.InstitutionAgent.bind_to_simulator
```

````

````{py:method} _bind_to_economy()
:canonical: pycityagent.agent.agent.InstitutionAgent._bind_to_economy
:async:

```{autodoc2-docstring} pycityagent.agent.agent.InstitutionAgent._bind_to_economy
```

````

````{py:method} handle_gather_message(payload: dict)
:canonical: pycityagent.agent.agent.InstitutionAgent.handle_gather_message
:async:

```{autodoc2-docstring} pycityagent.agent.agent.InstitutionAgent.handle_gather_message
```

````

````{py:method} gather_messages(agent_uuids: list[str], target: str) -> list[dict]
:canonical: pycityagent.agent.agent.InstitutionAgent.gather_messages
:async:

```{autodoc2-docstring} pycityagent.agent.agent.InstitutionAgent.gather_messages
```

````

````{py:property} mlflow_client
:canonical: pycityagent.agent.agent.InstitutionAgent.mlflow_client
:type: pycityagent.metrics.MlflowClient

```{autodoc2-docstring} pycityagent.agent.agent.InstitutionAgent.mlflow_client
```

````

````{py:method} set_mlflow_client(mlflow_client: pycityagent.metrics.MlflowClient)
:canonical: pycityagent.agent.agent.InstitutionAgent.set_mlflow_client

```{autodoc2-docstring} pycityagent.agent.agent.InstitutionAgent.set_mlflow_client
```

````

`````
