# {py:mod}`pycityagent.environment.sim.pause_service`

```{py:module} pycityagent.environment.sim.pause_service
```

```{autodoc2-docstring} pycityagent.environment.sim.pause_service
:allowtitles:
```

## Module Contents

### Classes

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`PauseService <pycityagent.environment.sim.pause_service.PauseService>`
  - ```{autodoc2-docstring} pycityagent.environment.sim.pause_service.PauseService
    :summary:
    ```
````

### Data

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`__all__ <pycityagent.environment.sim.pause_service.__all__>`
  - ```{autodoc2-docstring} pycityagent.environment.sim.pause_service.__all__
    :summary:
    ```
````

### API

````{py:data} __all__
:canonical: pycityagent.environment.sim.pause_service.__all__
:value: >
   ['PauseService']

```{autodoc2-docstring} pycityagent.environment.sim.pause_service.__all__
```

````

`````{py:class} PauseService(aio_channel: grpc.aio.Channel)
:canonical: pycityagent.environment.sim.pause_service.PauseService

```{autodoc2-docstring} pycityagent.environment.sim.pause_service.PauseService
```

```{rubric} Initialization
```

```{autodoc2-docstring} pycityagent.environment.sim.pause_service.PauseService.__init__
```

````{py:method} pause() -> collections.abc.Awaitable[typing.Union[dict[str, typing.Any], pycityproto.city.pause.v1.pause_service_pb2.PauseResponse]]
:canonical: pycityagent.environment.sim.pause_service.PauseService.pause
:async:

```{autodoc2-docstring} pycityagent.environment.sim.pause_service.PauseService.pause
```

````

````{py:method} resume() -> collections.abc.Awaitable[typing.Union[dict[str, typing.Any], pycityproto.city.pause.v1.pause_service_pb2.ResumeResponse]]
:canonical: pycityagent.environment.sim.pause_service.PauseService.resume
:async:

```{autodoc2-docstring} pycityagent.environment.sim.pause_service.PauseService.resume
```

````

`````
