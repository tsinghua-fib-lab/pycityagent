# {py:mod}`pycityagent.environment.sim.person_service`

```{py:module} pycityagent.environment.sim.person_service
```

```{autodoc2-docstring} pycityagent.environment.sim.person_service
:allowtitles:
```

## Module Contents

### Classes

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`PersonService <pycityagent.environment.sim.person_service.PersonService>`
  - ```{autodoc2-docstring} pycityagent.environment.sim.person_service.PersonService
    :summary:
    ```
````

### Data

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`__all__ <pycityagent.environment.sim.person_service.__all__>`
  - ```{autodoc2-docstring} pycityagent.environment.sim.person_service.__all__
    :summary:
    ```
````

### API

````{py:data} __all__
:canonical: pycityagent.environment.sim.person_service.__all__
:value: >
   ['PersonService']

```{autodoc2-docstring} pycityagent.environment.sim.person_service.__all__
```

````

`````{py:class} PersonService(aio_channel: grpc.aio.Channel)
:canonical: pycityagent.environment.sim.person_service.PersonService

```{autodoc2-docstring} pycityagent.environment.sim.person_service.PersonService
```

```{rubric} Initialization
```

```{autodoc2-docstring} pycityagent.environment.sim.person_service.PersonService.__init__
```

````{py:method} default_person() -> pycityproto.city.person.v2.person_pb2.Person
:canonical: pycityagent.environment.sim.person_service.PersonService.default_person
:staticmethod:

```{autodoc2-docstring} pycityagent.environment.sim.person_service.PersonService.default_person
```

````

````{py:method} default_dict_person() -> dict
:canonical: pycityagent.environment.sim.person_service.PersonService.default_dict_person
:staticmethod:

```{autodoc2-docstring} pycityagent.environment.sim.person_service.PersonService.default_dict_person
```

````

````{py:method} GetPerson(req: typing.Union[pycityproto.city.person.v2.person_service_pb2.GetPersonRequest, dict], dict_return: bool = True) -> collections.abc.Coroutine[typing.Any, typing.Any, typing.Union[dict[str, typing.Any], pycityproto.city.person.v2.person_service_pb2.GetPersonResponse]]
:canonical: pycityagent.environment.sim.person_service.PersonService.GetPerson

```{autodoc2-docstring} pycityagent.environment.sim.person_service.PersonService.GetPerson
```

````

````{py:method} AddPerson(req: typing.Union[pycityproto.city.person.v2.person_service_pb2.AddPersonRequest, dict], dict_return: bool = True) -> collections.abc.Coroutine[typing.Any, typing.Any, typing.Union[dict[str, typing.Any], pycityproto.city.person.v2.person_service_pb2.AddPersonResponse]]
:canonical: pycityagent.environment.sim.person_service.PersonService.AddPerson

```{autodoc2-docstring} pycityagent.environment.sim.person_service.PersonService.AddPerson
```

````

````{py:method} SetSchedule(req: typing.Union[pycityproto.city.person.v2.person_service_pb2.SetScheduleRequest, dict], dict_return: bool = True) -> collections.abc.Coroutine[typing.Any, typing.Any, typing.Union[dict[str, typing.Any], pycityproto.city.person.v2.person_service_pb2.SetScheduleResponse]]
:canonical: pycityagent.environment.sim.person_service.PersonService.SetSchedule

```{autodoc2-docstring} pycityagent.environment.sim.person_service.PersonService.SetSchedule
```

````

````{py:method} GetPersons(req: typing.Union[pycityproto.city.person.v2.person_service_pb2.GetPersonsRequest, dict], dict_return: bool = True) -> collections.abc.Coroutine[typing.Any, typing.Any, typing.Union[dict[str, typing.Any], pycityproto.city.person.v2.person_service_pb2.GetPersonsResponse]]
:canonical: pycityagent.environment.sim.person_service.PersonService.GetPersons

```{autodoc2-docstring} pycityagent.environment.sim.person_service.PersonService.GetPersons
```

````

````{py:method} GetPersonByLongLatBBox(req: typing.Union[pycityproto.city.person.v2.person_service_pb2.GetPersonByLongLatBBoxRequest, dict], dict_return: bool = True) -> collections.abc.Coroutine[typing.Any, typing.Any, typing.Union[dict[str, typing.Any], pycityproto.city.person.v2.person_service_pb2.GetPersonByLongLatBBoxResponse]]
:canonical: pycityagent.environment.sim.person_service.PersonService.GetPersonByLongLatBBox

```{autodoc2-docstring} pycityagent.environment.sim.person_service.PersonService.GetPersonByLongLatBBox
```

````

````{py:method} GetAllVehicles(req: typing.Union[pycityproto.city.person.v2.person_service_pb2.GetAllVehiclesRequest, dict], dict_return: bool = True) -> collections.abc.Coroutine[typing.Any, typing.Any, typing.Union[dict[str, typing.Any], pycityproto.city.person.v2.person_service_pb2.GetAllVehiclesResponse]]
:canonical: pycityagent.environment.sim.person_service.PersonService.GetAllVehicles

```{autodoc2-docstring} pycityagent.environment.sim.person_service.PersonService.GetAllVehicles
```

````

````{py:method} ResetPersonPosition(req: typing.Union[pycityproto.city.person.v2.person_service_pb2.ResetPersonPositionRequest, dict], dict_return: bool = True) -> collections.abc.Coroutine[typing.Any, typing.Any, typing.Union[dict[str, typing.Any], pycityproto.city.person.v2.person_service_pb2.ResetPersonPositionResponse]]
:canonical: pycityagent.environment.sim.person_service.PersonService.ResetPersonPosition

```{autodoc2-docstring} pycityagent.environment.sim.person_service.PersonService.ResetPersonPosition
```

````

````{py:method} SetControlledVehicleIDs(req: typing.Union[pycityproto.city.person.v2.person_service_pb2.SetControlledVehicleIDsRequest, dict], dict_return: bool = True) -> collections.abc.Coroutine[typing.Any, typing.Any, typing.Union[dict[str, typing.Any], pycityproto.city.person.v2.person_service_pb2.SetControlledVehicleIDsResponse]]
:canonical: pycityagent.environment.sim.person_service.PersonService.SetControlledVehicleIDs

```{autodoc2-docstring} pycityagent.environment.sim.person_service.PersonService.SetControlledVehicleIDs
```

````

````{py:method} FetchControlledVehicleEnvs(req: typing.Union[pycityproto.city.person.v2.person_service_pb2.FetchControlledVehicleEnvsRequest, dict], dict_return: bool = True) -> collections.abc.Coroutine[typing.Any, typing.Any, typing.Union[dict[str, typing.Any], pycityproto.city.person.v2.person_service_pb2.FetchControlledVehicleEnvsResponse]]
:canonical: pycityagent.environment.sim.person_service.PersonService.FetchControlledVehicleEnvs

```{autodoc2-docstring} pycityagent.environment.sim.person_service.PersonService.FetchControlledVehicleEnvs
```

````

````{py:method} SetControlledVehicleActions(req: typing.Union[pycityproto.city.person.v2.person_service_pb2.SetControlledVehicleActionsRequest, dict], dict_return: bool = True) -> collections.abc.Coroutine[typing.Any, typing.Any, typing.Union[dict[str, typing.Any], pycityproto.city.person.v2.person_service_pb2.SetControlledVehicleActionsResponse]]
:canonical: pycityagent.environment.sim.person_service.PersonService.SetControlledVehicleActions

```{autodoc2-docstring} pycityagent.environment.sim.person_service.PersonService.SetControlledVehicleActions
```

````

`````
