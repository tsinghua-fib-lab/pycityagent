# {py:mod}`agentsociety.environment.sim.sim_env`

```{py:module} agentsociety.environment.sim.sim_env
```

```{autodoc2-docstring} agentsociety.environment.sim.sim_env
:allowtitles:
```

## Module Contents

### Classes

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`ControlSimEnv <agentsociety.environment.sim.sim_env.ControlSimEnv>`
  - ```{autodoc2-docstring} agentsociety.environment.sim.sim_env.ControlSimEnv
    :summary:
    ```
````

### Functions

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`_generate_yaml_config <agentsociety.environment.sim.sim_env._generate_yaml_config>`
  - ```{autodoc2-docstring} agentsociety.environment.sim.sim_env._generate_yaml_config
    :summary:
    ```
````

### Data

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`__all__ <agentsociety.environment.sim.sim_env.__all__>`
  - ```{autodoc2-docstring} agentsociety.environment.sim.sim_env.__all__
    :summary:
    ```
````

### API

````{py:data} __all__
:canonical: agentsociety.environment.sim.sim_env.__all__
:value: >
   ['ControlSimEnv']

```{autodoc2-docstring} agentsociety.environment.sim.sim_env.__all__
```

````

````{py:function} _generate_yaml_config(map_file: str, max_day: int, start_step: int, total_step: int) -> str
:canonical: agentsociety.environment.sim.sim_env._generate_yaml_config

```{autodoc2-docstring} agentsociety.environment.sim.sim_env._generate_yaml_config
```
````

`````{py:class} ControlSimEnv(task_name: str, map_file: str, max_day: int, start_step: int, total_step: int, log_dir: str, primary_node_ip: str, min_step_time: int = 1000, timeout: int = 5, max_process: int = 32, sim_addr: typing.Optional[str] = None)
:canonical: agentsociety.environment.sim.sim_env.ControlSimEnv

```{autodoc2-docstring} agentsociety.environment.sim.sim_env.ControlSimEnv
```

```{rubric} Initialization
```

```{autodoc2-docstring} agentsociety.environment.sim.sim_env.ControlSimEnv.__init__
```

````{py:method} reset(sim_addr: typing.Optional[str] = None)
:canonical: agentsociety.environment.sim.sim_env.ControlSimEnv.reset

```{autodoc2-docstring} agentsociety.environment.sim.sim_env.ControlSimEnv.reset
```

````

````{py:method} close()
:canonical: agentsociety.environment.sim.sim_env.ControlSimEnv.close

```{autodoc2-docstring} agentsociety.environment.sim.sim_env.ControlSimEnv.close
```

````

`````
