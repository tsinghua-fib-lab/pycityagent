# {py:mod}`pycityagent.environment.utils.grpc`

```{py:module} pycityagent.environment.utils.grpc
```

```{autodoc2-docstring} pycityagent.environment.utils.grpc
:allowtitles:
```

## Module Contents

### Functions

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`create_channel <pycityagent.environment.utils.grpc.create_channel>`
  - ```{autodoc2-docstring} pycityagent.environment.utils.grpc.create_channel
    :summary:
    ```
* - {py:obj}`create_aio_channel <pycityagent.environment.utils.grpc.create_aio_channel>`
  - ```{autodoc2-docstring} pycityagent.environment.utils.grpc.create_aio_channel
    :summary:
    ```
````

### Data

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`__all__ <pycityagent.environment.utils.grpc.__all__>`
  - ```{autodoc2-docstring} pycityagent.environment.utils.grpc.__all__
    :summary:
    ```
````

### API

````{py:data} __all__
:canonical: pycityagent.environment.utils.grpc.__all__
:value: >
   ['create_channel', 'create_aio_channel']

```{autodoc2-docstring} pycityagent.environment.utils.grpc.__all__
```

````

````{py:function} create_channel(server_address: str, secure: bool = False) -> grpc.Channel
:canonical: pycityagent.environment.utils.grpc.create_channel

```{autodoc2-docstring} pycityagent.environment.utils.grpc.create_channel
```
````

````{py:function} create_aio_channel(server_address: str, secure: bool = False) -> grpc.aio.Channel
:canonical: pycityagent.environment.utils.grpc.create_aio_channel

```{autodoc2-docstring} pycityagent.environment.utils.grpc.create_aio_channel
```
````
