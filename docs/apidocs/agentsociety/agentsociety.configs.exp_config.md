# {py:mod}`agentsociety.configs.exp_config`

```{py:module} agentsociety.configs.exp_config
```

```{autodoc2-docstring} agentsociety.configs.exp_config
:allowtitles:
```

## Module Contents

### Classes

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`WorkflowStep <agentsociety.configs.exp_config.WorkflowStep>`
  -
* - {py:obj}`AgentConfig <agentsociety.configs.exp_config.AgentConfig>`
  -
* - {py:obj}`EnvironmentConfig <agentsociety.configs.exp_config.EnvironmentConfig>`
  -
* - {py:obj}`MessageInterceptConfig <agentsociety.configs.exp_config.MessageInterceptConfig>`
  -
* - {py:obj}`ExpConfig <agentsociety.configs.exp_config.ExpConfig>`
  -
````

### API

`````{py:class} WorkflowStep(/, **data: typing.Any)
:canonical: agentsociety.configs.exp_config.WorkflowStep

Bases: {py:obj}`pydantic.BaseModel`

````{py:attribute} type
:canonical: agentsociety.configs.exp_config.WorkflowStep.type
:type: agentsociety.utils.WorkflowType
:value: >
   None

```{autodoc2-docstring} agentsociety.configs.exp_config.WorkflowStep.type
```

````

````{py:attribute} days
:canonical: agentsociety.configs.exp_config.WorkflowStep.days
:type: int
:value: >
   'Field(...)'

```{autodoc2-docstring} agentsociety.configs.exp_config.WorkflowStep.days
```

````

````{py:attribute} times
:canonical: agentsociety.configs.exp_config.WorkflowStep.times
:type: int
:value: >
   'Field(...)'

```{autodoc2-docstring} agentsociety.configs.exp_config.WorkflowStep.times
```

````

````{py:attribute} description
:canonical: agentsociety.configs.exp_config.WorkflowStep.description
:type: str
:value: >
   'Field(...)'

```{autodoc2-docstring} agentsociety.configs.exp_config.WorkflowStep.description
```

````

````{py:attribute} func
:canonical: agentsociety.configs.exp_config.WorkflowStep.func
:type: typing.Optional[collections.abc.Callable]
:value: >
   None

```{autodoc2-docstring} agentsociety.configs.exp_config.WorkflowStep.func
```

````

`````

`````{py:class} AgentConfig(/, **data: typing.Any)
:canonical: agentsociety.configs.exp_config.AgentConfig

Bases: {py:obj}`pydantic.BaseModel`

````{py:attribute} number_of_citizen
:canonical: agentsociety.configs.exp_config.AgentConfig.number_of_citizen
:type: int
:value: >
   'Field(...)'

```{autodoc2-docstring} agentsociety.configs.exp_config.AgentConfig.number_of_citizen
```

````

````{py:attribute} number_of_firm
:canonical: agentsociety.configs.exp_config.AgentConfig.number_of_firm
:type: int
:value: >
   'Field(...)'

```{autodoc2-docstring} agentsociety.configs.exp_config.AgentConfig.number_of_firm
```

````

````{py:attribute} number_of_government
:canonical: agentsociety.configs.exp_config.AgentConfig.number_of_government
:type: int
:value: >
   'Field(...)'

```{autodoc2-docstring} agentsociety.configs.exp_config.AgentConfig.number_of_government
```

````

````{py:attribute} number_of_bank
:canonical: agentsociety.configs.exp_config.AgentConfig.number_of_bank
:type: int
:value: >
   'Field(...)'

```{autodoc2-docstring} agentsociety.configs.exp_config.AgentConfig.number_of_bank
```

````

````{py:attribute} number_of_nbs
:canonical: agentsociety.configs.exp_config.AgentConfig.number_of_nbs
:type: int
:value: >
   'Field(...)'

```{autodoc2-docstring} agentsociety.configs.exp_config.AgentConfig.number_of_nbs
```

````

````{py:attribute} group_size
:canonical: agentsociety.configs.exp_config.AgentConfig.group_size
:type: int
:value: >
   'Field(...)'

```{autodoc2-docstring} agentsociety.configs.exp_config.AgentConfig.group_size
```

````

````{py:attribute} embedding_model
:canonical: agentsociety.configs.exp_config.AgentConfig.embedding_model
:type: typing.Any
:value: >
   'Field(...)'

```{autodoc2-docstring} agentsociety.configs.exp_config.AgentConfig.embedding_model
```

````

````{py:attribute} agent_class_configs
:canonical: agentsociety.configs.exp_config.AgentConfig.agent_class_configs
:type: typing.Optional[dict[typing.Any, dict[str, typing.Any]]]
:value: >
   None

```{autodoc2-docstring} agentsociety.configs.exp_config.AgentConfig.agent_class_configs
```

````

````{py:attribute} memory_config_func
:canonical: agentsociety.configs.exp_config.AgentConfig.memory_config_func
:type: typing.Optional[dict[type[typing.Any], collections.abc.Callable]]
:value: >
   None

```{autodoc2-docstring} agentsociety.configs.exp_config.AgentConfig.memory_config_func
```

````

````{py:attribute} memory_config_init_func
:canonical: agentsociety.configs.exp_config.AgentConfig.memory_config_init_func
:type: typing.Optional[collections.abc.Callable]
:value: >
   'Field(...)'

```{autodoc2-docstring} agentsociety.configs.exp_config.AgentConfig.memory_config_init_func
```

````

````{py:attribute} init_func
:canonical: agentsociety.configs.exp_config.AgentConfig.init_func
:type: typing.Optional[list[collections.abc.Callable[[agentsociety.simulation.AgentSimulation], None]]]
:value: >
   None

```{autodoc2-docstring} agentsociety.configs.exp_config.AgentConfig.init_func
```

````

````{py:attribute} enable_institution
:canonical: agentsociety.configs.exp_config.AgentConfig.enable_institution
:type: bool
:value: >
   'Field(...)'

```{autodoc2-docstring} agentsociety.configs.exp_config.AgentConfig.enable_institution
```

````

````{py:method} create(number_of_citizen: int = 1, number_of_firm: int = 1, number_of_government: int = 1, number_of_bank: int = 1, number_of_nbs: int = 1, group_size: int = 100, embedding_model: typing.Any = None, agent_class_configs: typing.Optional[dict[typing.Any, dict[str, typing.Any]]] = None, enable_institution: bool = True, memory_config_func: typing.Optional[dict[type[typing.Any], collections.abc.Callable]] = None, memory_config_init_func: typing.Optional[collections.abc.Callable] = None, init_func: typing.Optional[list[collections.abc.Callable[[agentsociety.simulation.AgentSimulation], None]]] = None) -> agentsociety.configs.exp_config.AgentConfig
:canonical: agentsociety.configs.exp_config.AgentConfig.create
:classmethod:

```{autodoc2-docstring} agentsociety.configs.exp_config.AgentConfig.create
```

````

`````

`````{py:class} EnvironmentConfig(/, **data: typing.Any)
:canonical: agentsociety.configs.exp_config.EnvironmentConfig

Bases: {py:obj}`pydantic.BaseModel`

````{py:attribute} weather
:canonical: agentsociety.configs.exp_config.EnvironmentConfig.weather
:type: str
:value: >
   'Field(...)'

```{autodoc2-docstring} agentsociety.configs.exp_config.EnvironmentConfig.weather
```

````

````{py:attribute} crime
:canonical: agentsociety.configs.exp_config.EnvironmentConfig.crime
:type: str
:value: >
   'Field(...)'

```{autodoc2-docstring} agentsociety.configs.exp_config.EnvironmentConfig.crime
```

````

````{py:attribute} pollution
:canonical: agentsociety.configs.exp_config.EnvironmentConfig.pollution
:type: str
:value: >
   'Field(...)'

```{autodoc2-docstring} agentsociety.configs.exp_config.EnvironmentConfig.pollution
```

````

````{py:attribute} temperature
:canonical: agentsociety.configs.exp_config.EnvironmentConfig.temperature
:type: str
:value: >
   'Field(...)'

```{autodoc2-docstring} agentsociety.configs.exp_config.EnvironmentConfig.temperature
```

````

````{py:attribute} day
:canonical: agentsociety.configs.exp_config.EnvironmentConfig.day
:type: str
:value: >
   'Field(...)'

```{autodoc2-docstring} agentsociety.configs.exp_config.EnvironmentConfig.day
```

````

````{py:method} create(weather: str = 'The weather is normal', crime: str = 'The crime rate is low', pollution: str = 'The pollution level is low', temperature: str = 'The temperature is normal', day: str = 'Workday') -> agentsociety.configs.exp_config.EnvironmentConfig
:canonical: agentsociety.configs.exp_config.EnvironmentConfig.create
:classmethod:

```{autodoc2-docstring} agentsociety.configs.exp_config.EnvironmentConfig.create
```

````

`````

`````{py:class} MessageInterceptConfig(/, **data: typing.Any)
:canonical: agentsociety.configs.exp_config.MessageInterceptConfig

Bases: {py:obj}`pydantic.BaseModel`

````{py:attribute} mode
:canonical: agentsociety.configs.exp_config.MessageInterceptConfig.mode
:type: str
:value: >
   'Field(...)'

```{autodoc2-docstring} agentsociety.configs.exp_config.MessageInterceptConfig.mode
```

````

````{py:attribute} max_violation_time
:canonical: agentsociety.configs.exp_config.MessageInterceptConfig.max_violation_time
:type: int
:value: >
   'Field(...)'

```{autodoc2-docstring} agentsociety.configs.exp_config.MessageInterceptConfig.max_violation_time
```

````

````{py:method} create(mode: str, max_violation_time: int = 3) -> agentsociety.configs.exp_config.MessageInterceptConfig
:canonical: agentsociety.configs.exp_config.MessageInterceptConfig.create
:classmethod:

```{autodoc2-docstring} agentsociety.configs.exp_config.MessageInterceptConfig.create
```

````

`````

`````{py:class} ExpConfig(/, **data: typing.Any)
:canonical: agentsociety.configs.exp_config.ExpConfig

Bases: {py:obj}`pydantic.BaseModel`

````{py:attribute} agent_config
:canonical: agentsociety.configs.exp_config.ExpConfig.agent_config
:type: typing.Optional[agentsociety.configs.exp_config.AgentConfig]
:value: >
   None

```{autodoc2-docstring} agentsociety.configs.exp_config.ExpConfig.agent_config
```

````

````{py:attribute} workflow
:canonical: agentsociety.configs.exp_config.ExpConfig.workflow
:type: typing.Optional[list[agentsociety.configs.exp_config.WorkflowStep]]
:value: >
   None

```{autodoc2-docstring} agentsociety.configs.exp_config.ExpConfig.workflow
```

````

````{py:attribute} environment
:canonical: agentsociety.configs.exp_config.ExpConfig.environment
:type: typing.Optional[agentsociety.configs.exp_config.EnvironmentConfig]
:value: >
   'EnvironmentConfig(...)'

```{autodoc2-docstring} agentsociety.configs.exp_config.ExpConfig.environment
```

````

````{py:attribute} message_intercept
:canonical: agentsociety.configs.exp_config.ExpConfig.message_intercept
:type: typing.Optional[agentsociety.configs.exp_config.MessageInterceptConfig]
:value: >
   None

```{autodoc2-docstring} agentsociety.configs.exp_config.ExpConfig.message_intercept
```

````

````{py:attribute} metric_extractors
:canonical: agentsociety.configs.exp_config.ExpConfig.metric_extractors
:type: typing.Optional[list[tuple[int, collections.abc.Callable]]]
:value: >
   None

```{autodoc2-docstring} agentsociety.configs.exp_config.ExpConfig.metric_extractors
```

````

````{py:attribute} logging_level
:canonical: agentsociety.configs.exp_config.ExpConfig.logging_level
:type: int
:value: >
   'Field(...)'

```{autodoc2-docstring} agentsociety.configs.exp_config.ExpConfig.logging_level
```

````

````{py:attribute} exp_name
:canonical: agentsociety.configs.exp_config.ExpConfig.exp_name
:type: str
:value: >
   'Field(...)'

```{autodoc2-docstring} agentsociety.configs.exp_config.ExpConfig.exp_name
```

````

````{py:attribute} llm_semaphore
:canonical: agentsociety.configs.exp_config.ExpConfig.llm_semaphore
:type: int
:value: >
   'Field(...)'

```{autodoc2-docstring} agentsociety.configs.exp_config.ExpConfig.llm_semaphore
```

````

````{py:property} prop_agent_config
:canonical: agentsociety.configs.exp_config.ExpConfig.prop_agent_config
:type: agentsociety.configs.exp_config.AgentConfig

```{autodoc2-docstring} agentsociety.configs.exp_config.ExpConfig.prop_agent_config
```

````

````{py:property} prop_workflow
:canonical: agentsociety.configs.exp_config.ExpConfig.prop_workflow
:type: list[agentsociety.configs.exp_config.WorkflowStep]

```{autodoc2-docstring} agentsociety.configs.exp_config.ExpConfig.prop_workflow
```

````

````{py:property} prop_environment
:canonical: agentsociety.configs.exp_config.ExpConfig.prop_environment
:type: agentsociety.configs.exp_config.EnvironmentConfig

```{autodoc2-docstring} agentsociety.configs.exp_config.ExpConfig.prop_environment
```

````

````{py:property} prop_message_intercept
:canonical: agentsociety.configs.exp_config.ExpConfig.prop_message_intercept
:type: agentsociety.configs.exp_config.MessageInterceptConfig

```{autodoc2-docstring} agentsociety.configs.exp_config.ExpConfig.prop_message_intercept
```

````

````{py:property} prop_metric_extractors
:canonical: agentsociety.configs.exp_config.ExpConfig.prop_metric_extractors
:type: list[tuple[int, collections.abc.Callable]]

```{autodoc2-docstring} agentsociety.configs.exp_config.ExpConfig.prop_metric_extractors
```

````

````{py:method} SetAgentConfig(number_of_citizen: int = 1, number_of_firm: int = 1, number_of_government: int = 1, number_of_bank: int = 1, number_of_nbs: int = 1, group_size: int = 100, embedding_model: typing.Any = None, agent_class_configs: typing.Optional[dict[typing.Any, dict[str, list[dict]]]] = None, enable_institution: bool = True, memory_config_func: typing.Optional[dict[type[typing.Any], collections.abc.Callable]] = None, memory_config_init_func: typing.Optional[collections.abc.Callable] = None, init_func: typing.Optional[list[collections.abc.Callable[[agentsociety.simulation.AgentSimulation], None]]] = None) -> agentsociety.configs.exp_config.ExpConfig
:canonical: agentsociety.configs.exp_config.ExpConfig.SetAgentConfig

```{autodoc2-docstring} agentsociety.configs.exp_config.ExpConfig.SetAgentConfig
```

````

````{py:method} SetEnvironment(weather: str = 'The weather is normal', crime: str = 'The crime rate is low', pollution: str = 'The pollution level is low', temperature: str = 'The temperature is normal', day: str = 'Workday') -> agentsociety.configs.exp_config.ExpConfig
:canonical: agentsociety.configs.exp_config.ExpConfig.SetEnvironment

```{autodoc2-docstring} agentsociety.configs.exp_config.ExpConfig.SetEnvironment
```

````

````{py:method} SetMessageIntercept(mode: typing.Union[typing.Literal[point], typing.Literal[edge]], max_violation_time: int = 3) -> agentsociety.configs.exp_config.ExpConfig
:canonical: agentsociety.configs.exp_config.ExpConfig.SetMessageIntercept

```{autodoc2-docstring} agentsociety.configs.exp_config.ExpConfig.SetMessageIntercept
```

````

````{py:method} SetMetricExtractors(metric_extractors: list[tuple[int, collections.abc.Callable]])
:canonical: agentsociety.configs.exp_config.ExpConfig.SetMetricExtractors

```{autodoc2-docstring} agentsociety.configs.exp_config.ExpConfig.SetMetricExtractors
```

````

````{py:method} SetWorkFlow(workflows: list[agentsociety.configs.exp_config.WorkflowStep])
:canonical: agentsociety.configs.exp_config.ExpConfig.SetWorkFlow

```{autodoc2-docstring} agentsociety.configs.exp_config.ExpConfig.SetWorkFlow
```

````

`````
