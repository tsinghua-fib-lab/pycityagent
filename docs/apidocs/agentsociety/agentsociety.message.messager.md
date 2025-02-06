# {py:mod}`agentsociety.message.messager`

```{py:module} agentsociety.message.messager
```

```{autodoc2-docstring} agentsociety.message.messager
:allowtitles:
```

## Module Contents

### Classes

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`Messager <agentsociety.message.messager.Messager>`
  - ```{autodoc2-docstring} agentsociety.message.messager.Messager
    :summary:
    ```
````

### Data

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`__all__ <agentsociety.message.messager.__all__>`
  - ```{autodoc2-docstring} agentsociety.message.messager.__all__
    :summary:
    ```
* - {py:obj}`logger <agentsociety.message.messager.logger>`
  - ```{autodoc2-docstring} agentsociety.message.messager.logger
    :summary:
    ```
````

### API

````{py:data} __all__
:canonical: agentsociety.message.messager.__all__
:value: >
   ['Messager']

```{autodoc2-docstring} agentsociety.message.messager.__all__
```

````

````{py:data} logger
:canonical: agentsociety.message.messager.logger
:value: >
   'getLogger(...)'

```{autodoc2-docstring} agentsociety.message.messager.logger
```

````

`````{py:class} Messager(hostname: str, port: int = 1883, username=None, password=None, timeout=60, message_interceptor: typing.Optional[ray.ObjectRef] = None)
:canonical: agentsociety.message.messager.Messager

```{autodoc2-docstring} agentsociety.message.messager.Messager
```

```{rubric} Initialization
```

```{autodoc2-docstring} agentsociety.message.messager.Messager.__init__
```

````{py:property} message_interceptor
:canonical: agentsociety.message.messager.Messager.message_interceptor
:type: typing.Union[None, ray.ObjectRef]

```{autodoc2-docstring} agentsociety.message.messager.Messager.message_interceptor
```

````

````{py:method} get_log_list()
:canonical: agentsociety.message.messager.Messager.get_log_list

```{autodoc2-docstring} agentsociety.message.messager.Messager.get_log_list
```

````

````{py:method} clear_log_list()
:canonical: agentsociety.message.messager.Messager.clear_log_list

```{autodoc2-docstring} agentsociety.message.messager.Messager.clear_log_list
```

````

````{py:method} set_message_interceptor(message_interceptor: ray.ObjectRef)
:canonical: agentsociety.message.messager.Messager.set_message_interceptor

```{autodoc2-docstring} agentsociety.message.messager.Messager.set_message_interceptor
```

````

````{py:method} __aexit__(exc_type, exc_value, traceback)
:canonical: agentsociety.message.messager.Messager.__aexit__
:async:

```{autodoc2-docstring} agentsociety.message.messager.Messager.__aexit__
```

````

````{py:method} ping()
:canonical: agentsociety.message.messager.Messager.ping
:async:

```{autodoc2-docstring} agentsociety.message.messager.Messager.ping
```

````

````{py:method} connect()
:canonical: agentsociety.message.messager.Messager.connect
:async:

```{autodoc2-docstring} agentsociety.message.messager.Messager.connect
```

````

````{py:method} disconnect()
:canonical: agentsociety.message.messager.Messager.disconnect
:async:

```{autodoc2-docstring} agentsociety.message.messager.Messager.disconnect
```

````

````{py:method} is_connected()
:canonical: agentsociety.message.messager.Messager.is_connected
:async:

```{autodoc2-docstring} agentsociety.message.messager.Messager.is_connected
```

````

````{py:method} subscribe(topics: typing.Union[str, list[str]], agents: typing.Union[typing.Any, list[typing.Any]])
:canonical: agentsociety.message.messager.Messager.subscribe
:async:

```{autodoc2-docstring} agentsociety.message.messager.Messager.subscribe
```

````

````{py:method} receive_messages()
:canonical: agentsociety.message.messager.Messager.receive_messages
:async:

```{autodoc2-docstring} agentsociety.message.messager.Messager.receive_messages
```

````

````{py:method} fetch_messages()
:canonical: agentsociety.message.messager.Messager.fetch_messages
:async:

```{autodoc2-docstring} agentsociety.message.messager.Messager.fetch_messages
```

````

````{py:method} send_message(topic: str, payload: dict, from_uuid: typing.Optional[str] = None, to_uuid: typing.Optional[str] = None)
:canonical: agentsociety.message.messager.Messager.send_message
:async:

```{autodoc2-docstring} agentsociety.message.messager.Messager.send_message
```

````

````{py:method} start_listening()
:canonical: agentsociety.message.messager.Messager.start_listening
:async:

```{autodoc2-docstring} agentsociety.message.messager.Messager.start_listening
```

````

````{py:method} stop()
:canonical: agentsociety.message.messager.Messager.stop
:async:

```{autodoc2-docstring} agentsociety.message.messager.Messager.stop
```

````

`````
