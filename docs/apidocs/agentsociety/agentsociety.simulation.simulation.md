# {py:mod}`agentsociety.simulation.simulation`

```{py:module} agentsociety.simulation.simulation
```

```{autodoc2-docstring} agentsociety.simulation.simulation
:allowtitles:
```

## Module Contents

### Classes

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`AgentSimulation <agentsociety.simulation.simulation.AgentSimulation>`
  - ```{autodoc2-docstring} agentsociety.simulation.simulation.AgentSimulation
    :summary:
    ```
````

### Data

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`logger <agentsociety.simulation.simulation.logger>`
  - ```{autodoc2-docstring} agentsociety.simulation.simulation.logger
    :summary:
    ```
* - {py:obj}`__all__ <agentsociety.simulation.simulation.__all__>`
  - ```{autodoc2-docstring} agentsociety.simulation.simulation.__all__
    :summary:
    ```
````

### API

````{py:data} logger
:canonical: agentsociety.simulation.simulation.logger
:value: >
   'getLogger(...)'

```{autodoc2-docstring} agentsociety.simulation.simulation.logger
```

````

````{py:data} __all__
:canonical: agentsociety.simulation.simulation.__all__
:value: >
   ['AgentSimulation']

```{autodoc2-docstring} agentsociety.simulation.simulation.__all__
```

````

`````{py:class} AgentSimulation(config: agentsociety.configs.SimConfig, agent_class: typing.Union[None, type[agentsociety.agent.Agent], list[type[agentsociety.agent.Agent]]] = None, agent_class_configs: typing.Optional[dict] = None, metric_extractors: typing.Optional[list[tuple[int, collections.abc.Callable]]] = None, enable_institution: bool = True, agent_prefix: str = 'agent_', exp_name: str = 'default_experiment', logging_level: int = logging.WARNING)
:canonical: agentsociety.simulation.simulation.AgentSimulation

```{autodoc2-docstring} agentsociety.simulation.simulation.AgentSimulation
```

```{rubric} Initialization
```

```{autodoc2-docstring} agentsociety.simulation.simulation.AgentSimulation.__init__
```

````{py:method} run_from_config(config: agentsociety.configs.ExpConfig, sim_config: agentsociety.configs.SimConfig)
:canonical: agentsociety.simulation.simulation.AgentSimulation.run_from_config
:async:
:classmethod:

```{autodoc2-docstring} agentsociety.simulation.simulation.AgentSimulation.run_from_config
```

````

````{py:property} enable_avro
:canonical: agentsociety.simulation.simulation.AgentSimulation.enable_avro
:type: bool

```{autodoc2-docstring} agentsociety.simulation.simulation.AgentSimulation.enable_avro
```

````

````{py:property} enable_pgsql
:canonical: agentsociety.simulation.simulation.AgentSimulation.enable_pgsql
:type: bool

```{autodoc2-docstring} agentsociety.simulation.simulation.AgentSimulation.enable_pgsql
```

````

````{py:property} avro_path
:canonical: agentsociety.simulation.simulation.AgentSimulation.avro_path
:type: pathlib.Path

```{autodoc2-docstring} agentsociety.simulation.simulation.AgentSimulation.avro_path
```

````

````{py:property} economy_client
:canonical: agentsociety.simulation.simulation.AgentSimulation.economy_client

```{autodoc2-docstring} agentsociety.simulation.simulation.AgentSimulation.economy_client
```

````

````{py:property} groups
:canonical: agentsociety.simulation.simulation.AgentSimulation.groups

```{autodoc2-docstring} agentsociety.simulation.simulation.AgentSimulation.groups
```

````

````{py:property} agent_uuids
:canonical: agentsociety.simulation.simulation.AgentSimulation.agent_uuids

```{autodoc2-docstring} agentsociety.simulation.simulation.AgentSimulation.agent_uuids
```

````

````{py:property} agent_uuid2group
:canonical: agentsociety.simulation.simulation.AgentSimulation.agent_uuid2group

```{autodoc2-docstring} agentsociety.simulation.simulation.AgentSimulation.agent_uuid2group
```

````

````{py:property} messager
:canonical: agentsociety.simulation.simulation.AgentSimulation.messager
:type: ray.ObjectRef

```{autodoc2-docstring} agentsociety.simulation.simulation.AgentSimulation.messager
```

````

````{py:property} message_interceptor
:canonical: agentsociety.simulation.simulation.AgentSimulation.message_interceptor
:type: ray.ObjectRef

```{autodoc2-docstring} agentsociety.simulation.simulation.AgentSimulation.message_interceptor
```

````

````{py:method} _save_exp_info() -> None
:canonical: agentsociety.simulation.simulation.AgentSimulation._save_exp_info
:async:

```{autodoc2-docstring} agentsociety.simulation.simulation.AgentSimulation._save_exp_info
```

````

````{py:method} _update_exp_status(status: int, error: str = '') -> None
:canonical: agentsociety.simulation.simulation.AgentSimulation._update_exp_status
:async:

```{autodoc2-docstring} agentsociety.simulation.simulation.AgentSimulation._update_exp_status
```

````

````{py:method} _monitor_exp_status(stop_event: asyncio.Event)
:canonical: agentsociety.simulation.simulation.AgentSimulation._monitor_exp_status
:async:

```{autodoc2-docstring} agentsociety.simulation.simulation.AgentSimulation._monitor_exp_status
```

````

````{py:method} __aenter__()
:canonical: agentsociety.simulation.simulation.AgentSimulation.__aenter__
:async:

```{autodoc2-docstring} agentsociety.simulation.simulation.AgentSimulation.__aenter__
```

````

````{py:method} __aexit__(exc_type, exc_val, exc_tb)
:canonical: agentsociety.simulation.simulation.AgentSimulation.__aexit__
:async:

```{autodoc2-docstring} agentsociety.simulation.simulation.AgentSimulation.__aexit__
```

````

````{py:method} pause_simulator()
:canonical: agentsociety.simulation.simulation.AgentSimulation.pause_simulator
:async:

```{autodoc2-docstring} agentsociety.simulation.simulation.AgentSimulation.pause_simulator
```

````

````{py:method} resume_simulator()
:canonical: agentsociety.simulation.simulation.AgentSimulation.resume_simulator
:async:

```{autodoc2-docstring} agentsociety.simulation.simulation.AgentSimulation.resume_simulator
```

````

````{py:method} init_agents(agent_count: dict[type[agentsociety.agent.Agent], int], group_size: int = 10000, pg_sql_writers: int = 32, message_interceptors: int = 1, message_interceptor_blocks: typing.Optional[list[agentsociety.message.MessageBlockBase]] = None, social_black_list: typing.Optional[list[tuple[str, str]]] = None, message_listener: typing.Optional[agentsociety.message.MessageBlockListenerBase] = None, embedding_model: langchain_core.embeddings.Embeddings = SimpleEmbedding(), memory_config_init_func: typing.Optional[collections.abc.Callable] = None, memory_config_func: typing.Optional[dict[type[agentsociety.agent.Agent], collections.abc.Callable]] = None, environment: dict[str, str] = {}, llm_semaphore: int = 200) -> None
:canonical: agentsociety.simulation.simulation.AgentSimulation.init_agents
:async:

```{autodoc2-docstring} agentsociety.simulation.simulation.AgentSimulation.init_agents
```

````

````{py:method} gather(content: str, target_agent_uuids: typing.Optional[list[str]] = None)
:canonical: agentsociety.simulation.simulation.AgentSimulation.gather
:async:

```{autodoc2-docstring} agentsociety.simulation.simulation.AgentSimulation.gather
```

````

````{py:method} filter(types: typing.Optional[list[typing.Type[agentsociety.agent.Agent]]] = None, keys: typing.Optional[list[str]] = None, values: typing.Optional[list[typing.Any]] = None) -> list[str]
:canonical: agentsociety.simulation.simulation.AgentSimulation.filter
:async:

```{autodoc2-docstring} agentsociety.simulation.simulation.AgentSimulation.filter
```

````

````{py:method} update_environment(key: str, value: str)
:canonical: agentsociety.simulation.simulation.AgentSimulation.update_environment
:async:

```{autodoc2-docstring} agentsociety.simulation.simulation.AgentSimulation.update_environment
```

````

````{py:method} update(target_agent_uuid: str, target_key: str, content: typing.Any)
:canonical: agentsociety.simulation.simulation.AgentSimulation.update
:async:

```{autodoc2-docstring} agentsociety.simulation.simulation.AgentSimulation.update
```

````

````{py:method} economy_update(target_agent_id: int, target_key: str, content: typing.Any, mode: typing.Literal[replace, merge] = 'replace')
:canonical: agentsociety.simulation.simulation.AgentSimulation.economy_update
:async:

```{autodoc2-docstring} agentsociety.simulation.simulation.AgentSimulation.economy_update
```

````

````{py:method} send_survey(survey: agentsociety.survey.Survey, agent_uuids: list[str] = [])
:canonical: agentsociety.simulation.simulation.AgentSimulation.send_survey
:async:

```{autodoc2-docstring} agentsociety.simulation.simulation.AgentSimulation.send_survey
```

````

````{py:method} send_interview_message(content: str, agent_uuids: typing.Union[str, list[str]])
:canonical: agentsociety.simulation.simulation.AgentSimulation.send_interview_message
:async:

```{autodoc2-docstring} agentsociety.simulation.simulation.AgentSimulation.send_interview_message
```

````

````{py:method} extract_metric(metric_extractors: list[collections.abc.Callable])
:canonical: agentsociety.simulation.simulation.AgentSimulation.extract_metric
:async:

```{autodoc2-docstring} agentsociety.simulation.simulation.AgentSimulation.extract_metric
```

````

````{py:method} step()
:canonical: agentsociety.simulation.simulation.AgentSimulation.step
:async:

```{autodoc2-docstring} agentsociety.simulation.simulation.AgentSimulation.step
```

````

````{py:method} run(day: int = 1)
:canonical: agentsociety.simulation.simulation.AgentSimulation.run
:async:

```{autodoc2-docstring} agentsociety.simulation.simulation.AgentSimulation.run
```

````

`````
