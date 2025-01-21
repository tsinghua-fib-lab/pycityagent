# {py:mod}`pycityagent.utils.decorators`

```{py:module} pycityagent.utils.decorators
```

```{autodoc2-docstring} pycityagent.utils.decorators
:allowtitles:
```

## Module Contents

### Functions

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`record_call_aio <pycityagent.utils.decorators.record_call_aio>`
  - ```{autodoc2-docstring} pycityagent.utils.decorators.record_call_aio
    :summary:
    ```
* - {py:obj}`record_call <pycityagent.utils.decorators.record_call>`
  - ```{autodoc2-docstring} pycityagent.utils.decorators.record_call
    :summary:
    ```
* - {py:obj}`lock_decorator <pycityagent.utils.decorators.lock_decorator>`
  - ```{autodoc2-docstring} pycityagent.utils.decorators.lock_decorator
    :summary:
    ```
````

### Data

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`CALLING_STRING <pycityagent.utils.decorators.CALLING_STRING>`
  - ```{autodoc2-docstring} pycityagent.utils.decorators.CALLING_STRING
    :summary:
    ```
* - {py:obj}`__all__ <pycityagent.utils.decorators.__all__>`
  - ```{autodoc2-docstring} pycityagent.utils.decorators.__all__
    :summary:
    ```
````

### API

````{py:data} CALLING_STRING
:canonical: pycityagent.utils.decorators.CALLING_STRING
:value: >
   'function: `{func_name}` in "{file_path}", line {line_number}, arguments: `{arguments}` start time: `...'

```{autodoc2-docstring} pycityagent.utils.decorators.CALLING_STRING
```

````

````{py:data} __all__
:canonical: pycityagent.utils.decorators.__all__
:value: >
   ['record_call_aio', 'record_call', 'lock_decorator']

```{autodoc2-docstring} pycityagent.utils.decorators.__all__
```

````

````{py:function} record_call_aio(record_function_calling: bool = True)
:canonical: pycityagent.utils.decorators.record_call_aio

```{autodoc2-docstring} pycityagent.utils.decorators.record_call_aio
```
````

````{py:function} record_call(record_function_calling: bool = True)
:canonical: pycityagent.utils.decorators.record_call

```{autodoc2-docstring} pycityagent.utils.decorators.record_call
```
````

````{py:function} lock_decorator(func)
:canonical: pycityagent.utils.decorators.lock_decorator

```{autodoc2-docstring} pycityagent.utils.decorators.lock_decorator
```
````
