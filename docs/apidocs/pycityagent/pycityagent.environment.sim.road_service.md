# {py:mod}`pycityagent.environment.sim.road_service`

```{py:module} pycityagent.environment.sim.road_service
```

```{autodoc2-docstring} pycityagent.environment.sim.road_service
:allowtitles:
```

## Module Contents

### Classes

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`RoadService <pycityagent.environment.sim.road_service.RoadService>`
  - ```{autodoc2-docstring} pycityagent.environment.sim.road_service.RoadService
    :summary:
    ```
````

### Data

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`__all__ <pycityagent.environment.sim.road_service.__all__>`
  - ```{autodoc2-docstring} pycityagent.environment.sim.road_service.__all__
    :summary:
    ```
````

### API

````{py:data} __all__
:canonical: pycityagent.environment.sim.road_service.__all__
:value: >
   ['RoadService']

```{autodoc2-docstring} pycityagent.environment.sim.road_service.__all__
```

````

`````{py:class} RoadService(aio_channel: grpc.aio.Channel)
:canonical: pycityagent.environment.sim.road_service.RoadService

```{autodoc2-docstring} pycityagent.environment.sim.road_service.RoadService
```

```{rubric} Initialization
```

```{autodoc2-docstring} pycityagent.environment.sim.road_service.RoadService.__init__
```

````{py:method} GetRoad(req: typing.Union[pycityproto.city.map.v2.road_service_pb2.GetRoadRequest, dict], dict_return: bool = True) -> collections.abc.Coroutine[typing.Any, typing.Any, typing.Union[dict[str, typing.Any], pycityproto.city.map.v2.road_service_pb2.GetRoadResponse]]
:canonical: pycityagent.environment.sim.road_service.RoadService.GetRoad

```{autodoc2-docstring} pycityagent.environment.sim.road_service.RoadService.GetRoad
```

````

`````
