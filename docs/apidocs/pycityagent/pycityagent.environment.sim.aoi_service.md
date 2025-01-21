# {py:mod}`pycityagent.environment.sim.aoi_service`

```{py:module} pycityagent.environment.sim.aoi_service
```

```{autodoc2-docstring} pycityagent.environment.sim.aoi_service
:allowtitles:
```

## Module Contents

### Classes

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`AoiService <pycityagent.environment.sim.aoi_service.AoiService>`
  - ```{autodoc2-docstring} pycityagent.environment.sim.aoi_service.AoiService
    :summary:
    ```
````

### Data

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`__all__ <pycityagent.environment.sim.aoi_service.__all__>`
  - ```{autodoc2-docstring} pycityagent.environment.sim.aoi_service.__all__
    :summary:
    ```
````

### API

````{py:data} __all__
:canonical: pycityagent.environment.sim.aoi_service.__all__
:value: >
   ['AoiService']

```{autodoc2-docstring} pycityagent.environment.sim.aoi_service.__all__
```

````

`````{py:class} AoiService(aio_channel: grpc.aio.Channel)
:canonical: pycityagent.environment.sim.aoi_service.AoiService

```{autodoc2-docstring} pycityagent.environment.sim.aoi_service.AoiService
```

```{rubric} Initialization
```

```{autodoc2-docstring} pycityagent.environment.sim.aoi_service.AoiService.__init__
```

````{py:method} GetAoi(req: typing.Union[pycityproto.city.map.v2.aoi_service_pb2.GetAoiRequest, dict], dict_return: bool = True) -> collections.abc.Coroutine[typing.Any, typing.Any, typing.Union[typing.Dict[str, typing.Any], pycityproto.city.map.v2.aoi_service_pb2.GetAoiResponse]]
:canonical: pycityagent.environment.sim.aoi_service.AoiService.GetAoi

```{autodoc2-docstring} pycityagent.environment.sim.aoi_service.AoiService.GetAoi
```

````

`````
