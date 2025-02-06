# {py:mod}`agentsociety.environment.sim.lane_service`

```{py:module} agentsociety.environment.sim.lane_service
```

```{autodoc2-docstring} agentsociety.environment.sim.lane_service
:allowtitles:
```

## Module Contents

### Classes

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`LaneService <agentsociety.environment.sim.lane_service.LaneService>`
  - ```{autodoc2-docstring} agentsociety.environment.sim.lane_service.LaneService
    :summary:
    ```
````

### Data

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`__all__ <agentsociety.environment.sim.lane_service.__all__>`
  - ```{autodoc2-docstring} agentsociety.environment.sim.lane_service.__all__
    :summary:
    ```
````

### API

````{py:data} __all__
:canonical: agentsociety.environment.sim.lane_service.__all__
:value: >
   ['LaneService']

```{autodoc2-docstring} agentsociety.environment.sim.lane_service.__all__
```

````

`````{py:class} LaneService(aio_channel: grpc.aio.Channel)
:canonical: agentsociety.environment.sim.lane_service.LaneService

```{autodoc2-docstring} agentsociety.environment.sim.lane_service.LaneService
```

```{rubric} Initialization
```

```{autodoc2-docstring} agentsociety.environment.sim.lane_service.LaneService.__init__
```

````{py:method} GetLane(req: typing.Union[pycityproto.city.map.v2.lane_service_pb2.GetLaneRequest, dict], dict_return: bool = True) -> collections.abc.Coroutine[typing.Any, typing.Any, typing.Union[dict[str, typing.Any], pycityproto.city.map.v2.lane_service_pb2.GetLaneResponse]]
:canonical: agentsociety.environment.sim.lane_service.LaneService.GetLane

```{autodoc2-docstring} agentsociety.environment.sim.lane_service.LaneService.GetLane
```

````

````{py:method} SetLaneMaxV(req: typing.Union[pycityproto.city.map.v2.lane_service_pb2.SetLaneMaxVRequest, dict], dict_return: bool = True) -> collections.abc.Coroutine[typing.Any, typing.Any, typing.Union[dict[str, typing.Any], pycityproto.city.map.v2.lane_service_pb2.SetLaneMaxVResponse]]
:canonical: agentsociety.environment.sim.lane_service.LaneService.SetLaneMaxV

```{autodoc2-docstring} agentsociety.environment.sim.lane_service.LaneService.SetLaneMaxV
```

````

````{py:method} SetLaneRestriction(req: typing.Union[pycityproto.city.map.v2.lane_service_pb2.SetLaneRestrictionRequest, dict], dict_return: bool = True) -> collections.abc.Coroutine[typing.Any, typing.Any, typing.Union[dict[str, typing.Any], pycityproto.city.map.v2.lane_service_pb2.SetLaneRestrictionResponse]]
:canonical: agentsociety.environment.sim.lane_service.LaneService.SetLaneRestriction

```{autodoc2-docstring} agentsociety.environment.sim.lane_service.LaneService.SetLaneRestriction
```

````

````{py:method} GetLaneByLongLatBBox(req: typing.Union[pycityproto.city.map.v2.lane_service_pb2.GetLaneByLongLatBBoxRequest, dict], dict_return: bool = True) -> collections.abc.Coroutine[typing.Any, typing.Any, typing.Union[dict[str, typing.Any], pycityproto.city.map.v2.lane_service_pb2.GetLaneByLongLatBBoxResponse]]
:canonical: agentsociety.environment.sim.lane_service.LaneService.GetLaneByLongLatBBox

```{autodoc2-docstring} agentsociety.environment.sim.lane_service.LaneService.GetLaneByLongLatBBox
```

````

`````
