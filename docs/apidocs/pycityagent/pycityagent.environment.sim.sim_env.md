# {py:mod}`pycityagent.environment.sim.sim_env`

```{py:module} pycityagent.environment.sim.sim_env
```

```{autodoc2-docstring} pycityagent.environment.sim.sim_env
:allowtitles:
```

## Module Contents

### Classes

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`ControlSimEnv <pycityagent.environment.sim.sim_env.ControlSimEnv>`
  - ```{autodoc2-docstring} pycityagent.environment.sim.sim_env.ControlSimEnv
    :summary:
    ```
````

### Functions

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`_generate_yaml_config <pycityagent.environment.sim.sim_env._generate_yaml_config>`
  - ```{autodoc2-docstring} pycityagent.environment.sim.sim_env._generate_yaml_config
    :summary:
    ```
````

### Data

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`__all__ <pycityagent.environment.sim.sim_env.__all__>`
  - ```{autodoc2-docstring} pycityagent.environment.sim.sim_env.__all__
    :summary:
    ```
````

### API

````{py:data} __all__
:canonical: pycityagent.environment.sim.sim_env.__all__
:value: >
   ['ControlSimEnv']

```{autodoc2-docstring} pycityagent.environment.sim.sim_env.__all__
```

````

````{py:function} _generate_yaml_config(map_file: str, start_step: int, total_step: int) -> str
:canonical: pycityagent.environment.sim.sim_env._generate_yaml_config

```{autodoc2-docstring} pycityagent.environment.sim.sim_env._generate_yaml_config
```
````

`````{py:class} ControlSimEnv(task_name: str, map_file: str, start_step: int, total_step: int, log_dir: str, min_step_time: int = 1000, timeout: int = 5, sim_addr: typing.Optional[str] = None)
:canonical: pycityagent.environment.sim.sim_env.ControlSimEnv

```{autodoc2-docstring} pycityagent.environment.sim.sim_env.ControlSimEnv
```

```{rubric} Initialization
```

```{autodoc2-docstring} pycityagent.environment.sim.sim_env.ControlSimEnv.__init__
```

````{py:attribute} m
:canonical: pycityagent.environment.sim.sim_env.ControlSimEnv.m
:value: >
   'Map(...)'

```{autodoc2-docstring} pycityagent.environment.sim.sim_env.ControlSimEnv.m
```

````

````{py:method} reset(sim_addr: typing.Optional[str] = None)
:canonical: pycityagent.environment.sim.sim_env.ControlSimEnv.reset

```{autodoc2-docstring} pycityagent.environment.sim.sim_env.ControlSimEnv.reset
```

````

````{py:method} close()
:canonical: pycityagent.environment.sim.sim_env.ControlSimEnv.close

```{autodoc2-docstring} pycityagent.environment.sim.sim_env.ControlSimEnv.close
```

````

`````
