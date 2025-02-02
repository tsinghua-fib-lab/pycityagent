# {py:mod}`pycityagent.llm.llm`

```{py:module} pycityagent.llm.llm
```

```{autodoc2-docstring} pycityagent.llm.llm
:allowtitles:
```

## Module Contents

### Classes

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`LLM <pycityagent.llm.llm.LLM>`
  - ```{autodoc2-docstring} pycityagent.llm.llm.LLM
    :summary:
    ```
````

### Data

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`__all__ <pycityagent.llm.llm.__all__>`
  - ```{autodoc2-docstring} pycityagent.llm.llm.__all__
    :summary:
    ```
````

### API

````{py:data} __all__
:canonical: pycityagent.llm.llm.__all__
:value: >
   ['LLM']

```{autodoc2-docstring} pycityagent.llm.llm.__all__
```

````

`````{py:class} LLM(config: pycityagent.configs.LLMRequestConfig)
:canonical: pycityagent.llm.llm.LLM

```{autodoc2-docstring} pycityagent.llm.llm.LLM
```

```{rubric} Initialization
```

```{autodoc2-docstring} pycityagent.llm.llm.LLM.__init__
```

````{py:method} get_log_list()
:canonical: pycityagent.llm.llm.LLM.get_log_list

```{autodoc2-docstring} pycityagent.llm.llm.LLM.get_log_list
```

````

````{py:method} clear_log_list()
:canonical: pycityagent.llm.llm.LLM.clear_log_list

```{autodoc2-docstring} pycityagent.llm.llm.LLM.clear_log_list
```

````

````{py:method} set_semaphore(number_of_coroutine: int)
:canonical: pycityagent.llm.llm.LLM.set_semaphore

```{autodoc2-docstring} pycityagent.llm.llm.LLM.set_semaphore
```

````

````{py:method} clear_semaphore()
:canonical: pycityagent.llm.llm.LLM.clear_semaphore

```{autodoc2-docstring} pycityagent.llm.llm.LLM.clear_semaphore
```

````

````{py:method} clear_used()
:canonical: pycityagent.llm.llm.LLM.clear_used

```{autodoc2-docstring} pycityagent.llm.llm.LLM.clear_used
```

````

````{py:method} get_consumption()
:canonical: pycityagent.llm.llm.LLM.get_consumption

```{autodoc2-docstring} pycityagent.llm.llm.LLM.get_consumption
```

````

````{py:method} show_consumption(input_price: typing.Optional[float] = None, output_price: typing.Optional[float] = None)
:canonical: pycityagent.llm.llm.LLM.show_consumption

```{autodoc2-docstring} pycityagent.llm.llm.LLM.show_consumption
```

````

````{py:method} _get_next_client()
:canonical: pycityagent.llm.llm.LLM._get_next_client

```{autodoc2-docstring} pycityagent.llm.llm.LLM._get_next_client
```

````

````{py:method} atext_request(dialog: typing.Any, response_format: typing.Optional[dict[str, typing.Any]] = None, temperature: float = 1, max_tokens: typing.Optional[int] = None, top_p: typing.Optional[float] = None, frequency_penalty: typing.Optional[float] = None, presence_penalty: typing.Optional[float] = None, timeout: int = 300, retries=10, tools: typing.Optional[list[dict[str, typing.Any]]] = None, tool_choice: typing.Optional[dict[str, typing.Any]] = None)
:canonical: pycityagent.llm.llm.LLM.atext_request
:async:

```{autodoc2-docstring} pycityagent.llm.llm.LLM.atext_request
```

````

`````
