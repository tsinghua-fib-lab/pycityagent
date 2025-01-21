# {py:mod}`pycityagent.message.messager`

```{py:module} pycityagent.message.messager
```

```{autodoc2-docstring} pycityagent.message.messager
:allowtitles:
```

## Module Contents

### Classes

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`Messager <pycityagent.message.messager.Messager>`
  - ```{autodoc2-docstring} pycityagent.message.messager.Messager
    :summary:
    ```
````

### Data

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`logger <pycityagent.message.messager.logger>`
  - ```{autodoc2-docstring} pycityagent.message.messager.logger
    :summary:
    ```
````

### API

````{py:data} logger
:canonical: pycityagent.message.messager.logger
:value: >
   'getLogger(...)'

```{autodoc2-docstring} pycityagent.message.messager.logger
```

````

`````{py:class} Messager(hostname: str, port: int = 1883, username=None, password=None, timeout=60, message_interceptor: typing.Optional[ray.ObjectRef] = None)
:canonical: pycityagent.message.messager.Messager

```{autodoc2-docstring} pycityagent.message.messager.Messager
```

```{rubric} Initialization
```

```{autodoc2-docstring} pycityagent.message.messager.Messager.__init__
```

````{py:property} message_interceptor
:canonical: pycityagent.message.messager.Messager.message_interceptor
:type: typing.Union[None, ray.ObjectRef]

```{autodoc2-docstring} pycityagent.message.messager.Messager.message_interceptor
```

````

````{py:method} set_message_interceptor(message_interceptor: ray.ObjectRef)
:canonical: pycityagent.message.messager.Messager.set_message_interceptor

```{autodoc2-docstring} pycityagent.message.messager.Messager.set_message_interceptor
```

````

````{py:method} __aexit__(exc_type, exc_value, traceback)
:canonical: pycityagent.message.messager.Messager.__aexit__
:async:

```{autodoc2-docstring} pycityagent.message.messager.Messager.__aexit__
```

````

````{py:method} ping()
:canonical: pycityagent.message.messager.Messager.ping
:async:

```{autodoc2-docstring} pycityagent.message.messager.Messager.ping
```

````

````{py:method} connect()
:canonical: pycityagent.message.messager.Messager.connect
:async:

```{autodoc2-docstring} pycityagent.message.messager.Messager.connect
```

````

````{py:method} disconnect()
:canonical: pycityagent.message.messager.Messager.disconnect
:async:

```{autodoc2-docstring} pycityagent.message.messager.Messager.disconnect
```

````

````{py:method} is_connected()
:canonical: pycityagent.message.messager.Messager.is_connected
:async:

```{autodoc2-docstring} pycityagent.message.messager.Messager.is_connected
```

````

````{py:method} subscribe(topics: typing.Union[str, list[str]], agents: typing.Union[typing.Any, list[typing.Any]])
:canonical: pycityagent.message.messager.Messager.subscribe
:async:

```{autodoc2-docstring} pycityagent.message.messager.Messager.subscribe
```

````

````{py:method} receive_messages()
:canonical: pycityagent.message.messager.Messager.receive_messages
:async:

```{autodoc2-docstring} pycityagent.message.messager.Messager.receive_messages
```

````

````{py:method} fetch_messages()
:canonical: pycityagent.message.messager.Messager.fetch_messages
:async:

```{autodoc2-docstring} pycityagent.message.messager.Messager.fetch_messages
```

````

````{py:method} send_message(topic: str, payload: dict, from_uuid: typing.Optional[str] = None, to_uuid: typing.Optional[str] = None)
:canonical: pycityagent.message.messager.Messager.send_message
:async:

```{autodoc2-docstring} pycityagent.message.messager.Messager.send_message
```

````

````{py:method} start_listening()
:canonical: pycityagent.message.messager.Messager.start_listening
:async:

```{autodoc2-docstring} pycityagent.message.messager.Messager.start_listening
```

````

````{py:method} stop()
:canonical: pycityagent.message.messager.Messager.stop
:async:

```{autodoc2-docstring} pycityagent.message.messager.Messager.stop
```

````

`````
