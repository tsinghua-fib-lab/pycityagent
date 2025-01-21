# {py:mod}`pycityagent.economy.econ_client`

```{py:module} pycityagent.economy.econ_client
```

```{autodoc2-docstring} pycityagent.economy.econ_client
:allowtitles:
```

## Module Contents

### Classes

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`EconomyClient <pycityagent.economy.econ_client.EconomyClient>`
  - ```{autodoc2-docstring} pycityagent.economy.econ_client.EconomyClient
    :summary:
    ```
````

### Functions

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`_snake_to_pascal <pycityagent.economy.econ_client._snake_to_pascal>`
  - ```{autodoc2-docstring} pycityagent.economy.econ_client._snake_to_pascal
    :summary:
    ```
* - {py:obj}`_get_field_type_and_repeated <pycityagent.economy.econ_client._get_field_type_and_repeated>`
  - ```{autodoc2-docstring} pycityagent.economy.econ_client._get_field_type_and_repeated
    :summary:
    ```
* - {py:obj}`_create_aio_channel <pycityagent.economy.econ_client._create_aio_channel>`
  - ```{autodoc2-docstring} pycityagent.economy.econ_client._create_aio_channel
    :summary:
    ```
````

### Data

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`__all__ <pycityagent.economy.econ_client.__all__>`
  - ```{autodoc2-docstring} pycityagent.economy.econ_client.__all__
    :summary:
    ```
````

### API

````{py:data} __all__
:canonical: pycityagent.economy.econ_client.__all__
:value: >
   ['EconomyClient']

```{autodoc2-docstring} pycityagent.economy.econ_client.__all__
```

````

````{py:function} _snake_to_pascal(snake_str)
:canonical: pycityagent.economy.econ_client._snake_to_pascal

```{autodoc2-docstring} pycityagent.economy.econ_client._snake_to_pascal
```
````

````{py:function} _get_field_type_and_repeated(message, field_name: str) -> tuple[typing.Any, bool]
:canonical: pycityagent.economy.econ_client._get_field_type_and_repeated

```{autodoc2-docstring} pycityagent.economy.econ_client._get_field_type_and_repeated
```
````

````{py:function} _create_aio_channel(server_address: str, secure: bool = False) -> grpc.aio.Channel
:canonical: pycityagent.economy.econ_client._create_aio_channel

```{autodoc2-docstring} pycityagent.economy.econ_client._create_aio_channel
```
````

`````{py:class} EconomyClient(server_address: str, secure: bool = False)
:canonical: pycityagent.economy.econ_client.EconomyClient

```{autodoc2-docstring} pycityagent.economy.econ_client.EconomyClient
```

```{rubric} Initialization
```

```{autodoc2-docstring} pycityagent.economy.econ_client.EconomyClient.__init__
```

````{py:method} __getstate__()
:canonical: pycityagent.economy.econ_client.EconomyClient.__getstate__

```{autodoc2-docstring} pycityagent.economy.econ_client.EconomyClient.__getstate__
```

````

````{py:method} __setstate__(state)
:canonical: pycityagent.economy.econ_client.EconomyClient.__setstate__

```{autodoc2-docstring} pycityagent.economy.econ_client.EconomyClient.__setstate__
```

````

````{py:method} get(id: int, key: str) -> typing.Any
:canonical: pycityagent.economy.econ_client.EconomyClient.get
:async:

```{autodoc2-docstring} pycityagent.economy.econ_client.EconomyClient.get
```

````

````{py:method} update(id: int, key: str, value: typing.Any, mode: typing.Union[typing.Literal[replace], typing.Literal[merge]] = 'replace') -> typing.Any
:canonical: pycityagent.economy.econ_client.EconomyClient.update
:async:

```{autodoc2-docstring} pycityagent.economy.econ_client.EconomyClient.update
```

````

````{py:method} add_agents(configs: typing.Union[list[dict], dict])
:canonical: pycityagent.economy.econ_client.EconomyClient.add_agents
:async:

```{autodoc2-docstring} pycityagent.economy.econ_client.EconomyClient.add_agents
```

````

````{py:method} add_orgs(configs: typing.Union[list[dict], dict])
:canonical: pycityagent.economy.econ_client.EconomyClient.add_orgs
:async:

```{autodoc2-docstring} pycityagent.economy.econ_client.EconomyClient.add_orgs
```

````

````{py:method} calculate_taxes_due(org_id: int, agent_ids: list[int], incomes: list[float], enable_redistribution: bool)
:canonical: pycityagent.economy.econ_client.EconomyClient.calculate_taxes_due
:async:

```{autodoc2-docstring} pycityagent.economy.econ_client.EconomyClient.calculate_taxes_due
```

````

````{py:method} calculate_consumption(org_id: int, agent_ids: list[int], demands: list[int])
:canonical: pycityagent.economy.econ_client.EconomyClient.calculate_consumption
:async:

```{autodoc2-docstring} pycityagent.economy.econ_client.EconomyClient.calculate_consumption
```

````

````{py:method} calculate_interest(org_id: int, agent_ids: list[int])
:canonical: pycityagent.economy.econ_client.EconomyClient.calculate_interest
:async:

```{autodoc2-docstring} pycityagent.economy.econ_client.EconomyClient.calculate_interest
```

````

````{py:method} remove_agents(agent_ids: typing.Union[int, list[int]])
:canonical: pycityagent.economy.econ_client.EconomyClient.remove_agents
:async:

```{autodoc2-docstring} pycityagent.economy.econ_client.EconomyClient.remove_agents
```

````

````{py:method} remove_orgs(org_ids: typing.Union[int, list[int]])
:canonical: pycityagent.economy.econ_client.EconomyClient.remove_orgs
:async:

```{autodoc2-docstring} pycityagent.economy.econ_client.EconomyClient.remove_orgs
```

````

````{py:method} save(file_path: str) -> tuple[list[int], list[int]]
:canonical: pycityagent.economy.econ_client.EconomyClient.save
:async:

```{autodoc2-docstring} pycityagent.economy.econ_client.EconomyClient.save
```

````

````{py:method} load(file_path: str)
:canonical: pycityagent.economy.econ_client.EconomyClient.load
:async:

```{autodoc2-docstring} pycityagent.economy.econ_client.EconomyClient.load
```

````

````{py:method} get_org_entity_ids(org_type: pycityproto.city.economy.v2.economy_pb2.OrgType) -> list[int]
:canonical: pycityagent.economy.econ_client.EconomyClient.get_org_entity_ids
:async:

```{autodoc2-docstring} pycityagent.economy.econ_client.EconomyClient.get_org_entity_ids
```

````

````{py:method} add_delta_value(id: int, key: str, value: typing.Any) -> typing.Any
:canonical: pycityagent.economy.econ_client.EconomyClient.add_delta_value
:async:

```{autodoc2-docstring} pycityagent.economy.econ_client.EconomyClient.add_delta_value
```

````

`````
