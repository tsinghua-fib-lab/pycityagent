# {py:mod}`agentsociety.utils.decorators`

```{py:module} agentsociety.utils.decorators
```

```{autodoc2-docstring} agentsociety.utils.decorators
:allowtitles:
```

## Module Contents

### Functions

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`record_call_aio <agentsociety.utils.decorators.record_call_aio>`
  - ```{autodoc2-docstring} agentsociety.utils.decorators.record_call_aio
    :summary:
    ```
* - {py:obj}`record_call <agentsociety.utils.decorators.record_call>`
  - ```{autodoc2-docstring} agentsociety.utils.decorators.record_call
    :summary:
    ```
* - {py:obj}`lock_decorator <agentsociety.utils.decorators.lock_decorator>`
  - ```{autodoc2-docstring} agentsociety.utils.decorators.lock_decorator
    :summary:
    ```
````

### Data

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`CALLING_STRING <agentsociety.utils.decorators.CALLING_STRING>`
  - ```{autodoc2-docstring} agentsociety.utils.decorators.CALLING_STRING
    :summary:
    ```
* - {py:obj}`__all__ <agentsociety.utils.decorators.__all__>`
  - ```{autodoc2-docstring} agentsociety.utils.decorators.__all__
    :summary:
    ```
````

### API

````{py:data} CALLING_STRING
:canonical: agentsociety.utils.decorators.CALLING_STRING
:value: >
   'function: `{func_name}` in "{file_path}", line {line_number}, arguments: `{arguments}` start time: `...'

```{autodoc2-docstring} agentsociety.utils.decorators.CALLING_STRING
```

````

````{py:data} __all__
:canonical: agentsociety.utils.decorators.__all__
:value: >
   ['record_call_aio', 'record_call', 'lock_decorator']

```{autodoc2-docstring} agentsociety.utils.decorators.__all__
```

````

````{py:function} record_call_aio(record_function_calling: bool = True)
:canonical: agentsociety.utils.decorators.record_call_aio

```{autodoc2-docstring} agentsociety.utils.decorators.record_call_aio
```
````

````{py:function} record_call(record_function_calling: bool = True)
:canonical: agentsociety.utils.decorators.record_call

```{autodoc2-docstring} agentsociety.utils.decorators.record_call
```
````

````{py:function} lock_decorator(func)
:canonical: agentsociety.utils.decorators.lock_decorator

```{autodoc2-docstring} agentsociety.utils.decorators.lock_decorator
```
````
