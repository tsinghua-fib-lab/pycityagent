# {py:mod}`agentsociety.environment.sim.light_service`

```{py:module} agentsociety.environment.sim.light_service
```

```{autodoc2-docstring} agentsociety.environment.sim.light_service
:allowtitles:
```

## Module Contents

### Classes

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`LightService <agentsociety.environment.sim.light_service.LightService>`
  - ```{autodoc2-docstring} agentsociety.environment.sim.light_service.LightService
    :summary:
    ```
````

### Data

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`__all__ <agentsociety.environment.sim.light_service.__all__>`
  - ```{autodoc2-docstring} agentsociety.environment.sim.light_service.__all__
    :summary:
    ```
````

### API

````{py:data} __all__
:canonical: agentsociety.environment.sim.light_service.__all__
:value: >
   ['LightService']

```{autodoc2-docstring} agentsociety.environment.sim.light_service.__all__
```

````

`````{py:class} LightService(aio_channel: grpc.aio.Channel)
:canonical: agentsociety.environment.sim.light_service.LightService

```{autodoc2-docstring} agentsociety.environment.sim.light_service.LightService
```

```{rubric} Initialization
```

```{autodoc2-docstring} agentsociety.environment.sim.light_service.LightService.__init__
```

````{py:method} GetTrafficLight(req: typing.Union[pycityproto.city.map.v2.traffic_light_service_pb2.GetTrafficLightRequest, dict[str, typing.Any]], dict_return: bool = True) -> collections.abc.Coroutine[typing.Any, typing.Any, typing.Union[dict[str, typing.Any], pycityproto.city.map.v2.traffic_light_service_pb2.GetTrafficLightResponse]]
:canonical: agentsociety.environment.sim.light_service.LightService.GetTrafficLight

```{autodoc2-docstring} agentsociety.environment.sim.light_service.LightService.GetTrafficLight
```

````

````{py:method} SetTrafficLight(req: typing.Union[pycityproto.city.map.v2.traffic_light_service_pb2.SetTrafficLightRequest, dict[str, typing.Any]], dict_return: bool = True) -> collections.abc.Coroutine[typing.Any, typing.Any, typing.Union[dict[str, typing.Any], pycityproto.city.map.v2.traffic_light_service_pb2.SetTrafficLightResponse]]
:canonical: agentsociety.environment.sim.light_service.LightService.SetTrafficLight

```{autodoc2-docstring} agentsociety.environment.sim.light_service.LightService.SetTrafficLight
```

````

````{py:method} SetTrafficLightPhase(req: typing.Union[pycityproto.city.map.v2.traffic_light_service_pb2.SetTrafficLightPhaseRequest, dict], dict_return: bool = True) -> collections.abc.Coroutine[typing.Any, typing.Any, typing.Union[dict[str, typing.Any], pycityproto.city.map.v2.traffic_light_service_pb2.SetTrafficLightPhaseResponse]]
:canonical: agentsociety.environment.sim.light_service.LightService.SetTrafficLightPhase

```{autodoc2-docstring} agentsociety.environment.sim.light_service.LightService.SetTrafficLightPhase
```

````

````{py:method} SetTrafficLightStatus(req: typing.Union[pycityproto.city.map.v2.traffic_light_service_pb2.SetTrafficLightStatusRequest, dict], dict_return: bool = True) -> collections.abc.Coroutine[typing.Any, typing.Any, typing.Union[dict[str, typing.Any], pycityproto.city.map.v2.traffic_light_service_pb2.SetTrafficLightStatusResponse]]
:canonical: agentsociety.environment.sim.light_service.LightService.SetTrafficLightStatus

```{autodoc2-docstring} agentsociety.environment.sim.light_service.LightService.SetTrafficLightStatus
```

````

`````
