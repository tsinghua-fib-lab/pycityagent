# {py:mod}`pycityagent.environment.simulator`

```{py:module} pycityagent.environment.simulator
```

```{autodoc2-docstring} pycityagent.environment.simulator
:allowtitles:
```

## Module Contents

### Classes

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`CityMap <pycityagent.environment.simulator.CityMap>`
  - ```{autodoc2-docstring} pycityagent.environment.simulator.CityMap
    :summary:
    ```
* - {py:obj}`Simulator <pycityagent.environment.simulator.Simulator>`
  - ```{autodoc2-docstring} pycityagent.environment.simulator.Simulator
    :summary:
    ```
````

### Data

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`logger <pycityagent.environment.simulator.logger>`
  - ```{autodoc2-docstring} pycityagent.environment.simulator.logger
    :summary:
    ```
* - {py:obj}`__all__ <pycityagent.environment.simulator.__all__>`
  - ```{autodoc2-docstring} pycityagent.environment.simulator.__all__
    :summary:
    ```
````

### API

````{py:data} logger
:canonical: pycityagent.environment.simulator.logger
:value: >
   'getLogger(...)'

```{autodoc2-docstring} pycityagent.environment.simulator.logger
```

````

````{py:data} __all__
:canonical: pycityagent.environment.simulator.__all__
:value: >
   ['Simulator']

```{autodoc2-docstring} pycityagent.environment.simulator.__all__
```

````

`````{py:class} CityMap(mongo_input: tuple[str, str, str, str], map_cache_path: str)
:canonical: pycityagent.environment.simulator.CityMap

```{autodoc2-docstring} pycityagent.environment.simulator.CityMap
```

```{rubric} Initialization
```

```{autodoc2-docstring} pycityagent.environment.simulator.CityMap.__init__
```

````{py:method} get_aoi(aoi_id: typing.Optional[int] = None)
:canonical: pycityagent.environment.simulator.CityMap.get_aoi

```{autodoc2-docstring} pycityagent.environment.simulator.CityMap.get_aoi
```

````

````{py:method} get_poi(poi_id: typing.Optional[int] = None)
:canonical: pycityagent.environment.simulator.CityMap.get_poi

```{autodoc2-docstring} pycityagent.environment.simulator.CityMap.get_poi
```

````

````{py:method} query_pois(**kwargs)
:canonical: pycityagent.environment.simulator.CityMap.query_pois

```{autodoc2-docstring} pycityagent.environment.simulator.CityMap.query_pois
```

````

````{py:method} get_poi_cate()
:canonical: pycityagent.environment.simulator.CityMap.get_poi_cate

```{autodoc2-docstring} pycityagent.environment.simulator.CityMap.get_poi_cate
```

````

````{py:method} get_map()
:canonical: pycityagent.environment.simulator.CityMap.get_map

```{autodoc2-docstring} pycityagent.environment.simulator.CityMap.get_map
```

````

````{py:method} get_map_header()
:canonical: pycityagent.environment.simulator.CityMap.get_map_header

```{autodoc2-docstring} pycityagent.environment.simulator.CityMap.get_map_header
```

````

````{py:method} get_projector()
:canonical: pycityagent.environment.simulator.CityMap.get_projector

```{autodoc2-docstring} pycityagent.environment.simulator.CityMap.get_projector
```

````

`````

`````{py:class} Simulator(config: dict, create_map: bool = False)
:canonical: pycityagent.environment.simulator.Simulator

```{autodoc2-docstring} pycityagent.environment.simulator.Simulator
```

```{rubric} Initialization
```

```{autodoc2-docstring} pycityagent.environment.simulator.Simulator.__init__
```

````{py:attribute} config
:canonical: pycityagent.environment.simulator.Simulator.config
:value: >
   None

```{autodoc2-docstring} pycityagent.environment.simulator.Simulator.config
```

````

````{py:attribute} _map
:canonical: pycityagent.environment.simulator.Simulator._map
:value: >
   None

```{autodoc2-docstring} pycityagent.environment.simulator.Simulator._map
```

````

````{py:attribute} time
:canonical: pycityagent.environment.simulator.Simulator.time
:type: int
:value: >
   0

```{autodoc2-docstring} pycityagent.environment.simulator.Simulator.time
```

````

````{py:method} set_map(map: ray.ObjectRef)
:canonical: pycityagent.environment.simulator.Simulator.set_map

```{autodoc2-docstring} pycityagent.environment.simulator.Simulator.set_map
```

````

````{py:method} _create_poi_id_2_aoi_id()
:canonical: pycityagent.environment.simulator.Simulator._create_poi_id_2_aoi_id

```{autodoc2-docstring} pycityagent.environment.simulator.Simulator._create_poi_id_2_aoi_id
```

````

````{py:property} map
:canonical: pycityagent.environment.simulator.Simulator.map

```{autodoc2-docstring} pycityagent.environment.simulator.Simulator.map
```

````

````{py:method} get_log_list()
:canonical: pycityagent.environment.simulator.Simulator.get_log_list

```{autodoc2-docstring} pycityagent.environment.simulator.Simulator.get_log_list
```

````

````{py:method} clear_log_list()
:canonical: pycityagent.environment.simulator.Simulator.clear_log_list

```{autodoc2-docstring} pycityagent.environment.simulator.Simulator.clear_log_list
```

````

````{py:method} get_poi_cate()
:canonical: pycityagent.environment.simulator.Simulator.get_poi_cate

```{autodoc2-docstring} pycityagent.environment.simulator.Simulator.get_poi_cate
```

````

````{py:property} environment
:canonical: pycityagent.environment.simulator.Simulator.environment
:type: dict[str, str]

```{autodoc2-docstring} pycityagent.environment.simulator.Simulator.environment
```

````

````{py:method} get_server_addr()
:canonical: pycityagent.environment.simulator.Simulator.get_server_addr

```{autodoc2-docstring} pycityagent.environment.simulator.Simulator.get_server_addr
```

````

````{py:method} set_environment(environment: dict[str, str])
:canonical: pycityagent.environment.simulator.Simulator.set_environment

```{autodoc2-docstring} pycityagent.environment.simulator.Simulator.set_environment
```

````

````{py:method} sence(key: str) -> str
:canonical: pycityagent.environment.simulator.Simulator.sence

```{autodoc2-docstring} pycityagent.environment.simulator.Simulator.sence
```

````

````{py:method} update_environment(key: str, value: str)
:canonical: pycityagent.environment.simulator.Simulator.update_environment

```{autodoc2-docstring} pycityagent.environment.simulator.Simulator.update_environment
```

````

````{py:method} find_agents_by_area(req: dict, status=None)
:canonical: pycityagent.environment.simulator.Simulator.find_agents_by_area

```{autodoc2-docstring} pycityagent.environment.simulator.Simulator.find_agents_by_area
```

````

````{py:method} get_poi_categories(center: typing.Optional[typing.Union[tuple[float, float], shapely.geometry.Point]] = None, radius: typing.Optional[float] = None) -> list[str]
:canonical: pycityagent.environment.simulator.Simulator.get_poi_categories

```{autodoc2-docstring} pycityagent.environment.simulator.Simulator.get_poi_categories
```

````

````{py:method} get_time(format_time: bool = False, format: str = '%H:%M:%S') -> typing.Union[int, str]
:canonical: pycityagent.environment.simulator.Simulator.get_time
:async:

```{autodoc2-docstring} pycityagent.environment.simulator.Simulator.get_time
```

````

````{py:method} pause()
:canonical: pycityagent.environment.simulator.Simulator.pause
:async:

```{autodoc2-docstring} pycityagent.environment.simulator.Simulator.pause
```

````

````{py:method} resume()
:canonical: pycityagent.environment.simulator.Simulator.resume
:async:

```{autodoc2-docstring} pycityagent.environment.simulator.Simulator.resume
```

````

````{py:method} get_simulator_day() -> int
:canonical: pycityagent.environment.simulator.Simulator.get_simulator_day
:async:

```{autodoc2-docstring} pycityagent.environment.simulator.Simulator.get_simulator_day
```

````

````{py:method} get_simulator_second_from_start_of_day() -> int
:canonical: pycityagent.environment.simulator.Simulator.get_simulator_second_from_start_of_day
:async:

```{autodoc2-docstring} pycityagent.environment.simulator.Simulator.get_simulator_second_from_start_of_day
```

````

````{py:method} get_person(person_id: int) -> dict
:canonical: pycityagent.environment.simulator.Simulator.get_person
:async:

```{autodoc2-docstring} pycityagent.environment.simulator.Simulator.get_person
```

````

````{py:method} add_person(dict_person: dict) -> dict
:canonical: pycityagent.environment.simulator.Simulator.add_person
:async:

```{autodoc2-docstring} pycityagent.environment.simulator.Simulator.add_person
```

````

````{py:method} set_aoi_schedules(person_id: int, target_positions: typing.Union[list[typing.Union[int, tuple[int, int]]], typing.Union[int, tuple[int, int]]], departure_times: typing.Optional[list[float]] = None, modes: typing.Optional[list[mosstool.type.TripMode]] = None)
:canonical: pycityagent.environment.simulator.Simulator.set_aoi_schedules
:async:

```{autodoc2-docstring} pycityagent.environment.simulator.Simulator.set_aoi_schedules
```

````

````{py:method} reset_person_position(person_id: int, aoi_id: typing.Optional[int] = None, poi_id: typing.Optional[int] = None, lane_id: typing.Optional[int] = None, s: typing.Optional[float] = None)
:canonical: pycityagent.environment.simulator.Simulator.reset_person_position
:async:

```{autodoc2-docstring} pycityagent.environment.simulator.Simulator.reset_person_position
```

````

````{py:method} get_around_poi(center: typing.Union[tuple[float, float], shapely.geometry.Point], radius: float, poi_type: typing.Union[str, list[str]]) -> list[dict]
:canonical: pycityagent.environment.simulator.Simulator.get_around_poi

```{autodoc2-docstring} pycityagent.environment.simulator.Simulator.get_around_poi
```

````

`````
