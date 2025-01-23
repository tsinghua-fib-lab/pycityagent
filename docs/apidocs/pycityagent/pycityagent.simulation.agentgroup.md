# {py:mod}`pycityagent.simulation.agentgroup`

```{py:module} pycityagent.simulation.agentgroup
```

```{autodoc2-docstring} pycityagent.simulation.agentgroup
:allowtitles:
```

## Module Contents

### Classes

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`AgentGroup <pycityagent.simulation.agentgroup.AgentGroup>`
  - ```{autodoc2-docstring} pycityagent.simulation.agentgroup.AgentGroup
    :summary:
    ```
````

### Data

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`logger <pycityagent.simulation.agentgroup.logger>`
  - ```{autodoc2-docstring} pycityagent.simulation.agentgroup.logger
    :summary:
    ```
* - {py:obj}`__all__ <pycityagent.simulation.agentgroup.__all__>`
  - ```{autodoc2-docstring} pycityagent.simulation.agentgroup.__all__
    :summary:
    ```
````

### API

````{py:data} logger
:canonical: pycityagent.simulation.agentgroup.logger
:value: >
   'getLogger(...)'

```{autodoc2-docstring} pycityagent.simulation.agentgroup.logger
```

````

````{py:data} __all__
:canonical: pycityagent.simulation.agentgroup.__all__
:value: >
   ['AgentGroup']

```{autodoc2-docstring} pycityagent.simulation.agentgroup.__all__
```

````

`````{py:class} AgentGroup(agent_class: typing.Union[type[pycityagent.agent.Agent], list[type[pycityagent.agent.Agent]]], number_of_agents: typing.Union[int, list[int]], memory_config_function_group: dict[type[pycityagent.agent.Agent], collections.abc.Callable], config: dict, exp_name: str, exp_id: typing.Union[str, uuid.UUID], enable_avro: bool, avro_path: pathlib.Path, enable_pgsql: bool, pgsql_writer: ray.ObjectRef, message_interceptor: ray.ObjectRef, mlflow_run_id: str, embedding_model: langchain_core.embeddings.Embeddings, logging_level: int, agent_config_file: typing.Optional[dict[type[pycityagent.agent.Agent], str]] = None, environment: typing.Optional[dict[str, str]] = None)
:canonical: pycityagent.simulation.agentgroup.AgentGroup

```{autodoc2-docstring} pycityagent.simulation.agentgroup.AgentGroup
```

```{rubric} Initialization
```

```{autodoc2-docstring} pycityagent.simulation.agentgroup.AgentGroup.__init__
```

````{py:property} agent_count
:canonical: pycityagent.simulation.agentgroup.AgentGroup.agent_count

```{autodoc2-docstring} pycityagent.simulation.agentgroup.AgentGroup.agent_count
```

````

````{py:property} agent_uuids
:canonical: pycityagent.simulation.agentgroup.AgentGroup.agent_uuids

```{autodoc2-docstring} pycityagent.simulation.agentgroup.AgentGroup.agent_uuids
```

````

````{py:property} agent_type
:canonical: pycityagent.simulation.agentgroup.AgentGroup.agent_type

```{autodoc2-docstring} pycityagent.simulation.agentgroup.AgentGroup.agent_type
```

````

````{py:method} get_economy_ids()
:canonical: pycityagent.simulation.agentgroup.AgentGroup.get_economy_ids
:async:

```{autodoc2-docstring} pycityagent.simulation.agentgroup.AgentGroup.get_economy_ids
```

````

````{py:method} set_economy_ids(agent_ids: set[int], org_ids: set[int])
:canonical: pycityagent.simulation.agentgroup.AgentGroup.set_economy_ids
:async:

```{autodoc2-docstring} pycityagent.simulation.agentgroup.AgentGroup.set_economy_ids
```

````

````{py:method} get_agent_count()
:canonical: pycityagent.simulation.agentgroup.AgentGroup.get_agent_count

```{autodoc2-docstring} pycityagent.simulation.agentgroup.AgentGroup.get_agent_count
```

````

````{py:method} get_agent_uuids()
:canonical: pycityagent.simulation.agentgroup.AgentGroup.get_agent_uuids

```{autodoc2-docstring} pycityagent.simulation.agentgroup.AgentGroup.get_agent_uuids
```

````

````{py:method} get_agent_type()
:canonical: pycityagent.simulation.agentgroup.AgentGroup.get_agent_type

```{autodoc2-docstring} pycityagent.simulation.agentgroup.AgentGroup.get_agent_type
```

````

````{py:method} __aexit__(exc_type, exc_value, traceback)
:canonical: pycityagent.simulation.agentgroup.AgentGroup.__aexit__
:async:

```{autodoc2-docstring} pycityagent.simulation.agentgroup.AgentGroup.__aexit__
```

````

````{py:method} insert_agent()
:canonical: pycityagent.simulation.agentgroup.AgentGroup.insert_agent
:async:

```{autodoc2-docstring} pycityagent.simulation.agentgroup.AgentGroup.insert_agent
```

````

````{py:method} init_agents()
:canonical: pycityagent.simulation.agentgroup.AgentGroup.init_agents
:async:

```{autodoc2-docstring} pycityagent.simulation.agentgroup.AgentGroup.init_agents
```

````

````{py:method} filter(types: typing.Optional[list[typing.Type[pycityagent.agent.Agent]]] = None, keys: typing.Optional[list[str]] = None, values: typing.Optional[list[typing.Any]] = None) -> list[str]
:canonical: pycityagent.simulation.agentgroup.AgentGroup.filter
:async:

```{autodoc2-docstring} pycityagent.simulation.agentgroup.AgentGroup.filter
```

````

````{py:method} gather(content: str, target_agent_uuids: typing.Optional[list[str]] = None)
:canonical: pycityagent.simulation.agentgroup.AgentGroup.gather
:async:

```{autodoc2-docstring} pycityagent.simulation.agentgroup.AgentGroup.gather
```

````

````{py:method} update(target_agent_uuid: str, target_key: str, content: typing.Any)
:canonical: pycityagent.simulation.agentgroup.AgentGroup.update
:async:

```{autodoc2-docstring} pycityagent.simulation.agentgroup.AgentGroup.update
```

````

````{py:method} update_environment(key: str, value: str)
:canonical: pycityagent.simulation.agentgroup.AgentGroup.update_environment
:async:

```{autodoc2-docstring} pycityagent.simulation.agentgroup.AgentGroup.update_environment
```

````

````{py:method} message_dispatch()
:canonical: pycityagent.simulation.agentgroup.AgentGroup.message_dispatch
:async:

```{autodoc2-docstring} pycityagent.simulation.agentgroup.AgentGroup.message_dispatch
```

````

````{py:method} save_status(simulator_day: typing.Optional[int] = None, simulator_t: typing.Optional[int] = None)
:canonical: pycityagent.simulation.agentgroup.AgentGroup.save_status
:async:

```{autodoc2-docstring} pycityagent.simulation.agentgroup.AgentGroup.save_status
```

````

````{py:method} get_llm_consumption()
:canonical: pycityagent.simulation.agentgroup.AgentGroup.get_llm_consumption

```{autodoc2-docstring} pycityagent.simulation.agentgroup.AgentGroup.get_llm_consumption
```

````

````{py:method} step()
:canonical: pycityagent.simulation.agentgroup.AgentGroup.step
:async:

```{autodoc2-docstring} pycityagent.simulation.agentgroup.AgentGroup.step
```

````

````{py:method} save(day: int, t: int)
:canonical: pycityagent.simulation.agentgroup.AgentGroup.save
:async:

```{autodoc2-docstring} pycityagent.simulation.agentgroup.AgentGroup.save
```

````

`````
