# {py:mod}`pycityagent.environment.sim.social_service`

```{py:module} pycityagent.environment.sim.social_service
```

```{autodoc2-docstring} pycityagent.environment.sim.social_service
:allowtitles:
```

## Module Contents

### Classes

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`SocialService <pycityagent.environment.sim.social_service.SocialService>`
  - ```{autodoc2-docstring} pycityagent.environment.sim.social_service.SocialService
    :summary:
    ```
````

### Data

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`__all__ <pycityagent.environment.sim.social_service.__all__>`
  - ```{autodoc2-docstring} pycityagent.environment.sim.social_service.__all__
    :summary:
    ```
````

### API

````{py:data} __all__
:canonical: pycityagent.environment.sim.social_service.__all__
:value: >
   ['SocialService']

```{autodoc2-docstring} pycityagent.environment.sim.social_service.__all__
```

````

`````{py:class} SocialService(aio_channel: grpc.aio.Channel)
:canonical: pycityagent.environment.sim.social_service.SocialService

```{autodoc2-docstring} pycityagent.environment.sim.social_service.SocialService
```

```{rubric} Initialization
```

```{autodoc2-docstring} pycityagent.environment.sim.social_service.SocialService.__init__
```

````{py:method} Send(req: typing.Union[pycityproto.city.social.v1.social_service_pb2.SendRequest, dict], dict_return: bool = True) -> collections.abc.Coroutine[typing.Any, typing.Any, typing.Union[dict[str, typing.Any], pycityproto.city.social.v1.social_service_pb2.SendResponse]]
:canonical: pycityagent.environment.sim.social_service.SocialService.Send

```{autodoc2-docstring} pycityagent.environment.sim.social_service.SocialService.Send
```

````

````{py:method} Receive(req: typing.Union[pycityproto.city.social.v1.social_service_pb2.ReceiveRequest, dict], dict_return: bool = True) -> collections.abc.Coroutine[typing.Any, typing.Any, typing.Union[dict[str, typing.Any], pycityproto.city.social.v1.social_service_pb2.ReceiveResponse]]
:canonical: pycityagent.environment.sim.social_service.SocialService.Receive

```{autodoc2-docstring} pycityagent.environment.sim.social_service.SocialService.Receive
```

````

`````
