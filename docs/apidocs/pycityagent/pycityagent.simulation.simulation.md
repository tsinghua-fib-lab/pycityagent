# {py:mod}`pycityagent.simulation.simulation`

```{py:module} pycityagent.simulation.simulation
```

```{autodoc2-docstring} pycityagent.simulation.simulation
:allowtitles:
```

## Module Contents

### Classes

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`AgentSimulation <pycityagent.simulation.simulation.AgentSimulation>`
  - ```{autodoc2-docstring} pycityagent.simulation.simulation.AgentSimulation
    :summary:
    ```
````

### Data

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`logger <pycityagent.simulation.simulation.logger>`
  - ```{autodoc2-docstring} pycityagent.simulation.simulation.logger
    :summary:
    ```
* - {py:obj}`__all__ <pycityagent.simulation.simulation.__all__>`
  - ```{autodoc2-docstring} pycityagent.simulation.simulation.__all__
    :summary:
    ```
````

### API

````{py:data} logger
:canonical: pycityagent.simulation.simulation.logger
:value: >
   'getLogger(...)'

```{autodoc2-docstring} pycityagent.simulation.simulation.logger
```

````

````{py:data} __all__
:canonical: pycityagent.simulation.simulation.__all__
:value: >
   ['AgentSimulation']

```{autodoc2-docstring} pycityagent.simulation.simulation.__all__
```

````

`````{py:class} AgentSimulation(config: dict, agent_class: typing.Union[None, type[pycityagent.agent.Agent], list[type[pycityagent.agent.Agent]]] = None, agent_config_file: typing.Optional[dict] = None, metric_extractors: typing.Optional[list[tuple[int, collections.abc.Callable]]] = None, enable_institution: bool = True, agent_prefix: str = 'agent_', exp_name: str = 'default_experiment', logging_level: int = logging.WARNING)
:canonical: pycityagent.simulation.simulation.AgentSimulation

```{autodoc2-docstring} pycityagent.simulation.simulation.AgentSimulation
```

```{rubric} Initialization
```

```{autodoc2-docstring} pycityagent.simulation.simulation.AgentSimulation.__init__
```

````{py:method} run_from_config(config: dict)
:canonical: pycityagent.simulation.simulation.AgentSimulation.run_from_config
:async:
:classmethod:

```{autodoc2-docstring} pycityagent.simulation.simulation.AgentSimulation.run_from_config
```

````

````{py:property} enable_avro
:canonical: pycityagent.simulation.simulation.AgentSimulation.enable_avro
:type: bool

```{autodoc2-docstring} pycityagent.simulation.simulation.AgentSimulation.enable_avro
```

````

````{py:property} enable_pgsql
:canonical: pycityagent.simulation.simulation.AgentSimulation.enable_pgsql
:type: bool

```{autodoc2-docstring} pycityagent.simulation.simulation.AgentSimulation.enable_pgsql
```

````

````{py:property} avro_path
:canonical: pycityagent.simulation.simulation.AgentSimulation.avro_path
:type: pathlib.Path

```{autodoc2-docstring} pycityagent.simulation.simulation.AgentSimulation.avro_path
```

````

````{py:property} economy_client
:canonical: pycityagent.simulation.simulation.AgentSimulation.economy_client

```{autodoc2-docstring} pycityagent.simulation.simulation.AgentSimulation.economy_client
```

````

````{py:property} groups
:canonical: pycityagent.simulation.simulation.AgentSimulation.groups

```{autodoc2-docstring} pycityagent.simulation.simulation.AgentSimulation.groups
```

````

````{py:property} agent_uuids
:canonical: pycityagent.simulation.simulation.AgentSimulation.agent_uuids

```{autodoc2-docstring} pycityagent.simulation.simulation.AgentSimulation.agent_uuids
```

````

````{py:property} agent_uuid2group
:canonical: pycityagent.simulation.simulation.AgentSimulation.agent_uuid2group

```{autodoc2-docstring} pycityagent.simulation.simulation.AgentSimulation.agent_uuid2group
```

````

````{py:property} messager
:canonical: pycityagent.simulation.simulation.AgentSimulation.messager
:type: ray.ObjectRef

```{autodoc2-docstring} pycityagent.simulation.simulation.AgentSimulation.messager
```

````

````{py:property} message_interceptor
:canonical: pycityagent.simulation.simulation.AgentSimulation.message_interceptor
:type: ray.ObjectRef

```{autodoc2-docstring} pycityagent.simulation.simulation.AgentSimulation.message_interceptor
```

````

````{py:method} _save_exp_info() -> None
:canonical: pycityagent.simulation.simulation.AgentSimulation._save_exp_info
:async:

```{autodoc2-docstring} pycityagent.simulation.simulation.AgentSimulation._save_exp_info
```

````

````{py:method} _update_exp_status(status: int, error: str = '') -> None
:canonical: pycityagent.simulation.simulation.AgentSimulation._update_exp_status
:async:

```{autodoc2-docstring} pycityagent.simulation.simulation.AgentSimulation._update_exp_status
```

````

````{py:method} _monitor_exp_status(stop_event: asyncio.Event)
:canonical: pycityagent.simulation.simulation.AgentSimulation._monitor_exp_status
:async:

```{autodoc2-docstring} pycityagent.simulation.simulation.AgentSimulation._monitor_exp_status
```

````

````{py:method} __aenter__()
:canonical: pycityagent.simulation.simulation.AgentSimulation.__aenter__
:async:

```{autodoc2-docstring} pycityagent.simulation.simulation.AgentSimulation.__aenter__
```

````

````{py:method} __aexit__(exc_type, exc_val, exc_tb)
:canonical: pycityagent.simulation.simulation.AgentSimulation.__aexit__
:async:

```{autodoc2-docstring} pycityagent.simulation.simulation.AgentSimulation.__aexit__
```

````

````{py:method} pause_simulator()
:canonical: pycityagent.simulation.simulation.AgentSimulation.pause_simulator
:async:

```{autodoc2-docstring} pycityagent.simulation.simulation.AgentSimulation.pause_simulator
```

````

````{py:method} resume_simulator()
:canonical: pycityagent.simulation.simulation.AgentSimulation.resume_simulator
:async:

```{autodoc2-docstring} pycityagent.simulation.simulation.AgentSimulation.resume_simulator
```

````

````{py:method} init_agents(agent_count: dict[type[pycityagent.agent.Agent], int], group_size: int = 10000, pg_sql_writers: int = 32, message_interceptors: int = 1, message_interceptor_blocks: typing.Optional[list[pycityagent.message.MessageBlockBase]] = None, social_black_list: typing.Optional[list[tuple[str, str]]] = None, message_listener: typing.Optional[pycityagent.message.MessageBlockListenerBase] = None, embedding_model: langchain_core.embeddings.Embeddings = SimpleEmbedding(), memory_config_init_func: typing.Optional[collections.abc.Callable] = None, memory_config_func: typing.Optional[dict[type[pycityagent.agent.Agent], collections.abc.Callable]] = None, environment: dict[str, str] = {}, llm_semaphore: int = 200) -> None
:canonical: pycityagent.simulation.simulation.AgentSimulation.init_agents
:async:

```{autodoc2-docstring} pycityagent.simulation.simulation.AgentSimulation.init_agents
```

````

````{py:method} gather(content: str, target_agent_uuids: typing.Optional[list[str]] = None)
:canonical: pycityagent.simulation.simulation.AgentSimulation.gather
:async:

```{autodoc2-docstring} pycityagent.simulation.simulation.AgentSimulation.gather
```

````

````{py:method} filter(types: typing.Optional[list[typing.Type[pycityagent.agent.Agent]]] = None, keys: typing.Optional[list[str]] = None, values: typing.Optional[list[typing.Any]] = None) -> list[str]
:canonical: pycityagent.simulation.simulation.AgentSimulation.filter
:async:

```{autodoc2-docstring} pycityagent.simulation.simulation.AgentSimulation.filter
```

````

````{py:method} update_environment(key: str, value: str)
:canonical: pycityagent.simulation.simulation.AgentSimulation.update_environment
:async:

```{autodoc2-docstring} pycityagent.simulation.simulation.AgentSimulation.update_environment
```

````

````{py:method} update(target_agent_uuid: str, target_key: str, content: typing.Any)
:canonical: pycityagent.simulation.simulation.AgentSimulation.update
:async:

```{autodoc2-docstring} pycityagent.simulation.simulation.AgentSimulation.update
```

````

````{py:method} economy_update(target_agent_id: int, target_key: str, content: typing.Any, mode: typing.Literal[replace, merge] = 'replace')
:canonical: pycityagent.simulation.simulation.AgentSimulation.economy_update
:async:

```{autodoc2-docstring} pycityagent.simulation.simulation.AgentSimulation.economy_update
```

````

````{py:method} send_survey(survey: pycityagent.survey.Survey, agent_uuids: list[str] = [])
:canonical: pycityagent.simulation.simulation.AgentSimulation.send_survey
:async:

```{autodoc2-docstring} pycityagent.simulation.simulation.AgentSimulation.send_survey
```

````

````{py:method} send_interview_message(content: str, agent_uuids: typing.Union[str, list[str]])
:canonical: pycityagent.simulation.simulation.AgentSimulation.send_interview_message
:async:

```{autodoc2-docstring} pycityagent.simulation.simulation.AgentSimulation.send_interview_message
```

````

````{py:method} extract_metric(metric_extractors: list[collections.abc.Callable])
:canonical: pycityagent.simulation.simulation.AgentSimulation.extract_metric
:async:

```{autodoc2-docstring} pycityagent.simulation.simulation.AgentSimulation.extract_metric
```

````

````{py:method} step()
:canonical: pycityagent.simulation.simulation.AgentSimulation.step
:async:

```{autodoc2-docstring} pycityagent.simulation.simulation.AgentSimulation.step
```

````

````{py:method} run(day: int = 1)
:canonical: pycityagent.simulation.simulation.AgentSimulation.run
:async:

```{autodoc2-docstring} pycityagent.simulation.simulation.AgentSimulation.run
```

````

`````
