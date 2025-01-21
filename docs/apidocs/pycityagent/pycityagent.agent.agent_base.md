# {py:mod}`pycityagent.agent.agent_base`

```{py:module} pycityagent.agent.agent_base
```

```{autodoc2-docstring} pycityagent.agent.agent_base
:allowtitles:
```

## Module Contents

### Classes

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`AgentType <pycityagent.agent.agent_base.AgentType>`
  - ```{autodoc2-docstring} pycityagent.agent.agent_base.AgentType
    :summary:
    ```
* - {py:obj}`Agent <pycityagent.agent.agent_base.Agent>`
  - ```{autodoc2-docstring} pycityagent.agent.agent_base.Agent
    :summary:
    ```
````

### Data

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`logger <pycityagent.agent.agent_base.logger>`
  - ```{autodoc2-docstring} pycityagent.agent.agent_base.logger
    :summary:
    ```
````

### API

````{py:data} logger
:canonical: pycityagent.agent.agent_base.logger
:value: >
   'getLogger(...)'

```{autodoc2-docstring} pycityagent.agent.agent_base.logger
```

````

`````{py:class} AgentType
:canonical: pycityagent.agent.agent_base.AgentType

Bases: {py:obj}`enum.Enum`

```{autodoc2-docstring} pycityagent.agent.agent_base.AgentType
```

````{py:attribute} Unspecified
:canonical: pycityagent.agent.agent_base.AgentType.Unspecified
:value: >
   'Unspecified'

```{autodoc2-docstring} pycityagent.agent.agent_base.AgentType.Unspecified
```

````

````{py:attribute} Citizen
:canonical: pycityagent.agent.agent_base.AgentType.Citizen
:value: >
   'Citizen'

```{autodoc2-docstring} pycityagent.agent.agent_base.AgentType.Citizen
```

````

````{py:attribute} Institution
:canonical: pycityagent.agent.agent_base.AgentType.Institution
:value: >
   'Institution'

```{autodoc2-docstring} pycityagent.agent.agent_base.AgentType.Institution
```

````

`````

`````{py:class} Agent(name: str, type: pycityagent.agent.agent_base.AgentType = AgentType.Unspecified, llm_client: typing.Optional[pycityagent.llm.LLM] = None, economy_client: typing.Optional[pycityagent.economy.EconomyClient] = None, messager: typing.Optional[ray.ObjectRef] = None, message_interceptor: typing.Optional[ray.ObjectRef] = None, simulator: typing.Optional[pycityagent.environment.Simulator] = None, memory: typing.Optional[pycityagent.memory.Memory] = None, avro_file: typing.Optional[dict[str, str]] = None, copy_writer: typing.Optional[ray.ObjectRef] = None)
:canonical: pycityagent.agent.agent_base.Agent

Bases: {py:obj}`abc.ABC`

```{autodoc2-docstring} pycityagent.agent.agent_base.Agent
```

```{rubric} Initialization
```

```{autodoc2-docstring} pycityagent.agent.agent_base.Agent.__init__
```

````{py:attribute} configurable_fields
:canonical: pycityagent.agent.agent_base.Agent.configurable_fields
:type: list[str]
:value: >
   []

```{autodoc2-docstring} pycityagent.agent.agent_base.Agent.configurable_fields
```

````

````{py:attribute} default_values
:canonical: pycityagent.agent.agent_base.Agent.default_values
:type: dict[str, typing.Any]
:value: >
   None

```{autodoc2-docstring} pycityagent.agent.agent_base.Agent.default_values
```

````

````{py:attribute} fields_description
:canonical: pycityagent.agent.agent_base.Agent.fields_description
:type: dict[str, str]
:value: >
   None

```{autodoc2-docstring} pycityagent.agent.agent_base.Agent.fields_description
```

````

````{py:method} __getstate__()
:canonical: pycityagent.agent.agent_base.Agent.__getstate__

```{autodoc2-docstring} pycityagent.agent.agent_base.Agent.__getstate__
```

````

````{py:method} export_class_config() -> dict[str, dict]
:canonical: pycityagent.agent.agent_base.Agent.export_class_config
:classmethod:

```{autodoc2-docstring} pycityagent.agent.agent_base.Agent.export_class_config
```

````

````{py:method} _export_subblocks(block_cls: type[pycityagent.workflow.Block]) -> list[dict]
:canonical: pycityagent.agent.agent_base.Agent._export_subblocks
:classmethod:

```{autodoc2-docstring} pycityagent.agent.agent_base.Agent._export_subblocks
```

````

````{py:method} export_to_file(filepath: str) -> None
:canonical: pycityagent.agent.agent_base.Agent.export_to_file
:classmethod:

```{autodoc2-docstring} pycityagent.agent.agent_base.Agent.export_to_file
```

````

````{py:method} import_block_config(config: dict[str, typing.Union[list[dict], str]]) -> pycityagent.agent.agent_base.Agent
:canonical: pycityagent.agent.agent_base.Agent.import_block_config
:classmethod:

```{autodoc2-docstring} pycityagent.agent.agent_base.Agent.import_block_config
```

````

````{py:method} import_from_file(filepath: str) -> pycityagent.agent.agent_base.Agent
:canonical: pycityagent.agent.agent_base.Agent.import_from_file
:classmethod:

```{autodoc2-docstring} pycityagent.agent.agent_base.Agent.import_from_file
```

````

````{py:method} load_from_config(config: dict[str, list[dict]]) -> None
:canonical: pycityagent.agent.agent_base.Agent.load_from_config

```{autodoc2-docstring} pycityagent.agent.agent_base.Agent.load_from_config
```

````

````{py:method} load_from_file(filepath: str) -> None
:canonical: pycityagent.agent.agent_base.Agent.load_from_file

```{autodoc2-docstring} pycityagent.agent.agent_base.Agent.load_from_file
```

````

````{py:method} set_messager(messager: pycityagent.message.Messager)
:canonical: pycityagent.agent.agent_base.Agent.set_messager

```{autodoc2-docstring} pycityagent.agent.agent_base.Agent.set_messager
```

````

````{py:method} set_llm_client(llm_client: pycityagent.llm.LLM)
:canonical: pycityagent.agent.agent_base.Agent.set_llm_client

```{autodoc2-docstring} pycityagent.agent.agent_base.Agent.set_llm_client
```

````

````{py:method} set_simulator(simulator: pycityagent.environment.Simulator)
:canonical: pycityagent.agent.agent_base.Agent.set_simulator

```{autodoc2-docstring} pycityagent.agent.agent_base.Agent.set_simulator
```

````

````{py:method} set_economy_client(economy_client: pycityagent.economy.EconomyClient)
:canonical: pycityagent.agent.agent_base.Agent.set_economy_client

```{autodoc2-docstring} pycityagent.agent.agent_base.Agent.set_economy_client
```

````

````{py:method} set_memory(memory: pycityagent.memory.Memory)
:canonical: pycityagent.agent.agent_base.Agent.set_memory

```{autodoc2-docstring} pycityagent.agent.agent_base.Agent.set_memory
```

````

````{py:method} set_exp_id(exp_id: str)
:canonical: pycityagent.agent.agent_base.Agent.set_exp_id

```{autodoc2-docstring} pycityagent.agent.agent_base.Agent.set_exp_id
```

````

````{py:method} set_avro_file(avro_file: dict[str, str])
:canonical: pycityagent.agent.agent_base.Agent.set_avro_file

```{autodoc2-docstring} pycityagent.agent.agent_base.Agent.set_avro_file
```

````

````{py:method} set_pgsql_writer(pgsql_writer: ray.ObjectRef)
:canonical: pycityagent.agent.agent_base.Agent.set_pgsql_writer

```{autodoc2-docstring} pycityagent.agent.agent_base.Agent.set_pgsql_writer
```

````

````{py:method} set_message_interceptor(message_interceptor: ray.ObjectRef)
:canonical: pycityagent.agent.agent_base.Agent.set_message_interceptor

```{autodoc2-docstring} pycityagent.agent.agent_base.Agent.set_message_interceptor
```

````

````{py:property} uuid
:canonical: pycityagent.agent.agent_base.Agent.uuid

```{autodoc2-docstring} pycityagent.agent.agent_base.Agent.uuid
```

````

````{py:property} sim_id
:canonical: pycityagent.agent.agent_base.Agent.sim_id

```{autodoc2-docstring} pycityagent.agent.agent_base.Agent.sim_id
```

````

````{py:property} llm
:canonical: pycityagent.agent.agent_base.Agent.llm

```{autodoc2-docstring} pycityagent.agent.agent_base.Agent.llm
```

````

````{py:property} economy_client
:canonical: pycityagent.agent.agent_base.Agent.economy_client

```{autodoc2-docstring} pycityagent.agent.agent_base.Agent.economy_client
```

````

````{py:property} memory
:canonical: pycityagent.agent.agent_base.Agent.memory

```{autodoc2-docstring} pycityagent.agent.agent_base.Agent.memory
```

````

````{py:property} status
:canonical: pycityagent.agent.agent_base.Agent.status

```{autodoc2-docstring} pycityagent.agent.agent_base.Agent.status
```

````

````{py:property} stream
:canonical: pycityagent.agent.agent_base.Agent.stream

```{autodoc2-docstring} pycityagent.agent.agent_base.Agent.stream
```

````

````{py:property} simulator
:canonical: pycityagent.agent.agent_base.Agent.simulator

```{autodoc2-docstring} pycityagent.agent.agent_base.Agent.simulator
```

````

````{py:property} copy_writer
:canonical: pycityagent.agent.agent_base.Agent.copy_writer

```{autodoc2-docstring} pycityagent.agent.agent_base.Agent.copy_writer
```

````

````{py:property} messager
:canonical: pycityagent.agent.agent_base.Agent.messager

```{autodoc2-docstring} pycityagent.agent.agent_base.Agent.messager
```

````

````{py:method} messager_ping()
:canonical: pycityagent.agent.agent_base.Agent.messager_ping
:async:

```{autodoc2-docstring} pycityagent.agent.agent_base.Agent.messager_ping
```

````

````{py:method} generate_user_survey_response(survey: dict) -> str
:canonical: pycityagent.agent.agent_base.Agent.generate_user_survey_response
:async:

```{autodoc2-docstring} pycityagent.agent.agent_base.Agent.generate_user_survey_response
```

````

````{py:method} _process_survey(survey: dict)
:canonical: pycityagent.agent.agent_base.Agent._process_survey
:async:

```{autodoc2-docstring} pycityagent.agent.agent_base.Agent._process_survey
```

````

````{py:method} generate_user_chat_response(question: str) -> str
:canonical: pycityagent.agent.agent_base.Agent.generate_user_chat_response
:async:

```{autodoc2-docstring} pycityagent.agent.agent_base.Agent.generate_user_chat_response
```

````

````{py:method} _process_interview(payload: dict)
:canonical: pycityagent.agent.agent_base.Agent._process_interview
:async:

```{autodoc2-docstring} pycityagent.agent.agent_base.Agent._process_interview
```

````

````{py:method} process_agent_chat_response(payload: dict) -> str
:canonical: pycityagent.agent.agent_base.Agent.process_agent_chat_response
:async:

```{autodoc2-docstring} pycityagent.agent.agent_base.Agent.process_agent_chat_response
```

````

````{py:method} _process_agent_chat(payload: dict)
:canonical: pycityagent.agent.agent_base.Agent._process_agent_chat
:async:

```{autodoc2-docstring} pycityagent.agent.agent_base.Agent._process_agent_chat
```

````

````{py:method} handle_agent_chat_message(payload: dict)
:canonical: pycityagent.agent.agent_base.Agent.handle_agent_chat_message
:async:

```{autodoc2-docstring} pycityagent.agent.agent_base.Agent.handle_agent_chat_message
```

````

````{py:method} handle_user_chat_message(payload: dict)
:canonical: pycityagent.agent.agent_base.Agent.handle_user_chat_message
:async:

```{autodoc2-docstring} pycityagent.agent.agent_base.Agent.handle_user_chat_message
```

````

````{py:method} handle_user_survey_message(payload: dict)
:canonical: pycityagent.agent.agent_base.Agent.handle_user_survey_message
:async:

```{autodoc2-docstring} pycityagent.agent.agent_base.Agent.handle_user_survey_message
```

````

````{py:method} handle_gather_message(payload: typing.Any)
:canonical: pycityagent.agent.agent_base.Agent.handle_gather_message
:abstractmethod:
:async:

```{autodoc2-docstring} pycityagent.agent.agent_base.Agent.handle_gather_message
```

````

````{py:method} _send_message(to_agent_uuid: str, payload: dict, sub_topic: str)
:canonical: pycityagent.agent.agent_base.Agent._send_message
:async:

```{autodoc2-docstring} pycityagent.agent.agent_base.Agent._send_message
```

````

````{py:method} send_message_to_agent(to_agent_uuid: str, content: str, type: str = 'social')
:canonical: pycityagent.agent.agent_base.Agent.send_message_to_agent
:async:

```{autodoc2-docstring} pycityagent.agent.agent_base.Agent.send_message_to_agent
```

````

````{py:method} forward() -> None
:canonical: pycityagent.agent.agent_base.Agent.forward
:abstractmethod:
:async:

```{autodoc2-docstring} pycityagent.agent.agent_base.Agent.forward
```

````

````{py:method} run() -> None
:canonical: pycityagent.agent.agent_base.Agent.run
:async:

```{autodoc2-docstring} pycityagent.agent.agent_base.Agent.run
```

````

`````
