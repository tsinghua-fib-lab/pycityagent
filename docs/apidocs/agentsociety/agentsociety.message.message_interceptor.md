# {py:mod}`agentsociety.message.message_interceptor`

```{py:module} agentsociety.message.message_interceptor
```

```{autodoc2-docstring} agentsociety.message.message_interceptor
:allowtitles:
```

## Module Contents

### Classes

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`MessageBlockBase <agentsociety.message.message_interceptor.MessageBlockBase>`
  - ```{autodoc2-docstring} agentsociety.message.message_interceptor.MessageBlockBase
    :summary:
    ```
* - {py:obj}`MessageInterceptor <agentsociety.message.message_interceptor.MessageInterceptor>`
  - ```{autodoc2-docstring} agentsociety.message.message_interceptor.MessageInterceptor
    :summary:
    ```
* - {py:obj}`MessageBlockListenerBase <agentsociety.message.message_interceptor.MessageBlockListenerBase>`
  - ```{autodoc2-docstring} agentsociety.message.message_interceptor.MessageBlockListenerBase
    :summary:
    ```
````

### Data

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`DEFAULT_ERROR_STRING <agentsociety.message.message_interceptor.DEFAULT_ERROR_STRING>`
  - ```{autodoc2-docstring} agentsociety.message.message_interceptor.DEFAULT_ERROR_STRING
    :summary:
    ```
* - {py:obj}`logger <agentsociety.message.message_interceptor.logger>`
  - ```{autodoc2-docstring} agentsociety.message.message_interceptor.logger
    :summary:
    ```
* - {py:obj}`__all__ <agentsociety.message.message_interceptor.__all__>`
  - ```{autodoc2-docstring} agentsociety.message.message_interceptor.__all__
    :summary:
    ```
````

### API

````{py:data} DEFAULT_ERROR_STRING
:canonical: agentsociety.message.message_interceptor.DEFAULT_ERROR_STRING
:value: <Multiline-String>

```{autodoc2-docstring} agentsociety.message.message_interceptor.DEFAULT_ERROR_STRING
```

````

````{py:data} logger
:canonical: agentsociety.message.message_interceptor.logger
:value: >
   'getLogger(...)'

```{autodoc2-docstring} agentsociety.message.message_interceptor.logger
```

````

````{py:data} __all__
:canonical: agentsociety.message.message_interceptor.__all__
:value: >
   ['MessageBlockBase', 'MessageInterceptor', 'MessageBlockListenerBase']

```{autodoc2-docstring} agentsociety.message.message_interceptor.__all__
```

````

`````{py:class} MessageBlockBase(name: str = '')
:canonical: agentsociety.message.message_interceptor.MessageBlockBase

Bases: {py:obj}`abc.ABC`

```{autodoc2-docstring} agentsociety.message.message_interceptor.MessageBlockBase
```

```{rubric} Initialization
```

```{autodoc2-docstring} agentsociety.message.message_interceptor.MessageBlockBase.__init__
```

````{py:property} llm
:canonical: agentsociety.message.message_interceptor.MessageBlockBase.llm
:type: agentsociety.llm.LLM

```{autodoc2-docstring} agentsociety.message.message_interceptor.MessageBlockBase.llm
```

````

````{py:property} name
:canonical: agentsociety.message.message_interceptor.MessageBlockBase.name

```{autodoc2-docstring} agentsociety.message.message_interceptor.MessageBlockBase.name
```

````

````{py:property} has_llm
:canonical: agentsociety.message.message_interceptor.MessageBlockBase.has_llm
:type: bool

```{autodoc2-docstring} agentsociety.message.message_interceptor.MessageBlockBase.has_llm
```

````

````{py:method} set_llm(llm: agentsociety.llm.LLM)
:canonical: agentsociety.message.message_interceptor.MessageBlockBase.set_llm
:async:

```{autodoc2-docstring} agentsociety.message.message_interceptor.MessageBlockBase.set_llm
```

````

````{py:method} set_name(name: str)
:canonical: agentsociety.message.message_interceptor.MessageBlockBase.set_name
:async:

```{autodoc2-docstring} agentsociety.message.message_interceptor.MessageBlockBase.set_name
```

````

````{py:method} forward(from_uuid: str, to_uuid: str, msg: str, violation_counts: dict[str, int], black_list: list[tuple[str, str]]) -> tuple[bool, str]
:canonical: agentsociety.message.message_interceptor.MessageBlockBase.forward
:async:

```{autodoc2-docstring} agentsociety.message.message_interceptor.MessageBlockBase.forward
```

````

`````

`````{py:class} MessageInterceptor(blocks: typing.Optional[list[agentsociety.message.message_interceptor.MessageBlockBase]] = None, black_list: typing.Optional[list[tuple[str, str]]] = None, llm_config: typing.Optional[agentsociety.configs.LLMRequestConfig] = None, queue: typing.Optional[ray.util.queue.Queue] = None)
:canonical: agentsociety.message.message_interceptor.MessageInterceptor

```{autodoc2-docstring} agentsociety.message.message_interceptor.MessageInterceptor
```

```{rubric} Initialization
```

```{autodoc2-docstring} agentsociety.message.message_interceptor.MessageInterceptor.__init__
```

````{py:property} llm
:canonical: agentsociety.message.message_interceptor.MessageInterceptor.llm
:type: agentsociety.llm.LLM

```{autodoc2-docstring} agentsociety.message.message_interceptor.MessageInterceptor.llm
```

````

````{py:method} blocks() -> list[agentsociety.message.message_interceptor.MessageBlockBase]
:canonical: agentsociety.message.message_interceptor.MessageInterceptor.blocks
:async:

```{autodoc2-docstring} agentsociety.message.message_interceptor.MessageInterceptor.blocks
```

````

````{py:method} set_llm(llm: agentsociety.llm.LLM)
:canonical: agentsociety.message.message_interceptor.MessageInterceptor.set_llm
:async:

```{autodoc2-docstring} agentsociety.message.message_interceptor.MessageInterceptor.set_llm
```

````

````{py:method} violation_counts() -> dict[str, int]
:canonical: agentsociety.message.message_interceptor.MessageInterceptor.violation_counts
:async:

```{autodoc2-docstring} agentsociety.message.message_interceptor.MessageInterceptor.violation_counts
```

````

````{py:property} has_llm
:canonical: agentsociety.message.message_interceptor.MessageInterceptor.has_llm
:type: bool

```{autodoc2-docstring} agentsociety.message.message_interceptor.MessageInterceptor.has_llm
```

````

````{py:method} black_list() -> list[tuple[str, str]]
:canonical: agentsociety.message.message_interceptor.MessageInterceptor.black_list
:async:

```{autodoc2-docstring} agentsociety.message.message_interceptor.MessageInterceptor.black_list
```

````

````{py:method} add_to_black_list(black_list: typing.Union[list[tuple[str, str]], tuple[str, str]])
:canonical: agentsociety.message.message_interceptor.MessageInterceptor.add_to_black_list
:async:

```{autodoc2-docstring} agentsociety.message.message_interceptor.MessageInterceptor.add_to_black_list
```

````

````{py:property} has_queue
:canonical: agentsociety.message.message_interceptor.MessageInterceptor.has_queue
:type: bool

```{autodoc2-docstring} agentsociety.message.message_interceptor.MessageInterceptor.has_queue
```

````

````{py:method} set_queue(queue: ray.util.queue.Queue)
:canonical: agentsociety.message.message_interceptor.MessageInterceptor.set_queue
:async:

```{autodoc2-docstring} agentsociety.message.message_interceptor.MessageInterceptor.set_queue
```

````

````{py:method} remove_from_black_list(to_remove_black_list: typing.Union[list[tuple[str, str]], tuple[str, str]])
:canonical: agentsociety.message.message_interceptor.MessageInterceptor.remove_from_black_list
:async:

```{autodoc2-docstring} agentsociety.message.message_interceptor.MessageInterceptor.remove_from_black_list
```

````

````{py:property} queue
:canonical: agentsociety.message.message_interceptor.MessageInterceptor.queue
:type: ray.util.queue.Queue

```{autodoc2-docstring} agentsociety.message.message_interceptor.MessageInterceptor.queue
```

````

````{py:method} insert_block(block: agentsociety.message.message_interceptor.MessageBlockBase, index: typing.Optional[int] = None)
:canonical: agentsociety.message.message_interceptor.MessageInterceptor.insert_block
:async:

```{autodoc2-docstring} agentsociety.message.message_interceptor.MessageInterceptor.insert_block
```

````

````{py:method} pop_block(index: typing.Optional[int] = None) -> agentsociety.message.message_interceptor.MessageBlockBase
:canonical: agentsociety.message.message_interceptor.MessageInterceptor.pop_block
:async:

```{autodoc2-docstring} agentsociety.message.message_interceptor.MessageInterceptor.pop_block
```

````

````{py:method} set_black_list(black_list: typing.Union[list[tuple[str, str]], tuple[str, str]])
:canonical: agentsociety.message.message_interceptor.MessageInterceptor.set_black_list
:async:

```{autodoc2-docstring} agentsociety.message.message_interceptor.MessageInterceptor.set_black_list
```

````

````{py:method} set_blocks(blocks: list[agentsociety.message.message_interceptor.MessageBlockBase])
:canonical: agentsociety.message.message_interceptor.MessageInterceptor.set_blocks
:async:

```{autodoc2-docstring} agentsociety.message.message_interceptor.MessageInterceptor.set_blocks
```

````

````{py:method} forward(from_uuid: str, to_uuid: str, msg: str)
:canonical: agentsociety.message.message_interceptor.MessageInterceptor.forward
:async:

```{autodoc2-docstring} agentsociety.message.message_interceptor.MessageInterceptor.forward
```

````

`````

`````{py:class} MessageBlockListenerBase(save_queue_values: bool = False, get_queue_period: float = 0.1)
:canonical: agentsociety.message.message_interceptor.MessageBlockListenerBase

Bases: {py:obj}`abc.ABC`

```{autodoc2-docstring} agentsociety.message.message_interceptor.MessageBlockListenerBase
```

```{rubric} Initialization
```

```{autodoc2-docstring} agentsociety.message.message_interceptor.MessageBlockListenerBase.__init__
```

````{py:property} queue
:canonical: agentsociety.message.message_interceptor.MessageBlockListenerBase.queue
:type: ray.util.queue.Queue

```{autodoc2-docstring} agentsociety.message.message_interceptor.MessageBlockListenerBase.queue
```

````

````{py:property} has_queue
:canonical: agentsociety.message.message_interceptor.MessageBlockListenerBase.has_queue
:type: bool

```{autodoc2-docstring} agentsociety.message.message_interceptor.MessageBlockListenerBase.has_queue
```

````

````{py:method} set_queue(queue: ray.util.queue.Queue)
:canonical: agentsociety.message.message_interceptor.MessageBlockListenerBase.set_queue
:async:

```{autodoc2-docstring} agentsociety.message.message_interceptor.MessageBlockListenerBase.set_queue
```

````

````{py:method} forward()
:canonical: agentsociety.message.message_interceptor.MessageBlockListenerBase.forward
:async:

```{autodoc2-docstring} agentsociety.message.message_interceptor.MessageBlockListenerBase.forward
```

````

`````
