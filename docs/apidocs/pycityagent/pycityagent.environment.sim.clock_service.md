# {py:mod}`pycityagent.environment.sim.clock_service`

```{py:module} pycityagent.environment.sim.clock_service
```

```{autodoc2-docstring} pycityagent.environment.sim.clock_service
:allowtitles:
```

## Module Contents

### Classes

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`ClockService <pycityagent.environment.sim.clock_service.ClockService>`
  - ```{autodoc2-docstring} pycityagent.environment.sim.clock_service.ClockService
    :summary:
    ```
````

### Data

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`__all__ <pycityagent.environment.sim.clock_service.__all__>`
  - ```{autodoc2-docstring} pycityagent.environment.sim.clock_service.__all__
    :summary:
    ```
````

### API

````{py:data} __all__
:canonical: pycityagent.environment.sim.clock_service.__all__
:value: >
   ['ClockService']

```{autodoc2-docstring} pycityagent.environment.sim.clock_service.__all__
```

````

`````{py:class} ClockService(aio_channel: grpc.aio.Channel)
:canonical: pycityagent.environment.sim.clock_service.ClockService

```{autodoc2-docstring} pycityagent.environment.sim.clock_service.ClockService
```

```{rubric} Initialization
```

```{autodoc2-docstring} pycityagent.environment.sim.clock_service.ClockService.__init__
```

````{py:method} Now(req: typing.Union[pycityproto.city.clock.v1.clock_service_pb2.NowRequest, dict], dict_return: bool = True) -> collections.abc.Coroutine[typing.Any, typing.Any, typing.Union[typing.Dict[str, typing.Any], pycityproto.city.clock.v1.clock_service_pb2.NowResponse]]
:canonical: pycityagent.environment.sim.clock_service.ClockService.Now

```{autodoc2-docstring} pycityagent.environment.sim.clock_service.ClockService.Now
```

````

`````
