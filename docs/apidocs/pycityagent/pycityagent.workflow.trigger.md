# {py:mod}`pycityagent.workflow.trigger`

```{py:module} pycityagent.workflow.trigger
```

```{autodoc2-docstring} pycityagent.workflow.trigger
:allowtitles:
```

## Module Contents

### Classes

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`EventTrigger <pycityagent.workflow.trigger.EventTrigger>`
  - ```{autodoc2-docstring} pycityagent.workflow.trigger.EventTrigger
    :summary:
    ```
* - {py:obj}`MemoryChangeTrigger <pycityagent.workflow.trigger.MemoryChangeTrigger>`
  - ```{autodoc2-docstring} pycityagent.workflow.trigger.MemoryChangeTrigger
    :summary:
    ```
* - {py:obj}`TimeTrigger <pycityagent.workflow.trigger.TimeTrigger>`
  - ```{autodoc2-docstring} pycityagent.workflow.trigger.TimeTrigger
    :summary:
    ```
````

### Data

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`KEY_TRIGGER_COMPONENTS <pycityagent.workflow.trigger.KEY_TRIGGER_COMPONENTS>`
  - ```{autodoc2-docstring} pycityagent.workflow.trigger.KEY_TRIGGER_COMPONENTS
    :summary:
    ```
* - {py:obj}`__all__ <pycityagent.workflow.trigger.__all__>`
  - ```{autodoc2-docstring} pycityagent.workflow.trigger.__all__
    :summary:
    ```
````

### API

````{py:data} KEY_TRIGGER_COMPONENTS
:canonical: pycityagent.workflow.trigger.KEY_TRIGGER_COMPONENTS
:value: >
   None

```{autodoc2-docstring} pycityagent.workflow.trigger.KEY_TRIGGER_COMPONENTS
```

````

````{py:data} __all__
:canonical: pycityagent.workflow.trigger.__all__
:value: >
   ['EventTrigger', 'MemoryChangeTrigger', 'TimeTrigger']

```{autodoc2-docstring} pycityagent.workflow.trigger.__all__
```

````

`````{py:class} EventTrigger(block=None)
:canonical: pycityagent.workflow.trigger.EventTrigger

```{autodoc2-docstring} pycityagent.workflow.trigger.EventTrigger
```

```{rubric} Initialization
```

```{autodoc2-docstring} pycityagent.workflow.trigger.EventTrigger.__init__
```

````{py:attribute} required_components
:canonical: pycityagent.workflow.trigger.EventTrigger.required_components
:type: list[type]
:value: >
   []

```{autodoc2-docstring} pycityagent.workflow.trigger.EventTrigger.required_components
```

````

````{py:method} initialize() -> None
:canonical: pycityagent.workflow.trigger.EventTrigger.initialize

```{autodoc2-docstring} pycityagent.workflow.trigger.EventTrigger.initialize
```

````

````{py:method} wait_for_trigger() -> None
:canonical: pycityagent.workflow.trigger.EventTrigger.wait_for_trigger
:abstractmethod:
:async:

```{autodoc2-docstring} pycityagent.workflow.trigger.EventTrigger.wait_for_trigger
```

````

`````

`````{py:class} MemoryChangeTrigger(key: str)
:canonical: pycityagent.workflow.trigger.MemoryChangeTrigger

Bases: {py:obj}`pycityagent.workflow.trigger.EventTrigger`

```{autodoc2-docstring} pycityagent.workflow.trigger.MemoryChangeTrigger
```

```{rubric} Initialization
```

```{autodoc2-docstring} pycityagent.workflow.trigger.MemoryChangeTrigger.__init__
```

````{py:attribute} required_components
:canonical: pycityagent.workflow.trigger.MemoryChangeTrigger.required_components
:value: >
   None

```{autodoc2-docstring} pycityagent.workflow.trigger.MemoryChangeTrigger.required_components
```

````

````{py:method} initialize() -> None
:canonical: pycityagent.workflow.trigger.MemoryChangeTrigger.initialize

```{autodoc2-docstring} pycityagent.workflow.trigger.MemoryChangeTrigger.initialize
```

````

````{py:method} wait_for_trigger() -> None
:canonical: pycityagent.workflow.trigger.MemoryChangeTrigger.wait_for_trigger
:async:

```{autodoc2-docstring} pycityagent.workflow.trigger.MemoryChangeTrigger.wait_for_trigger
```

````

`````

`````{py:class} TimeTrigger(days: typing.Optional[int] = None, hours: typing.Optional[int] = None, minutes: typing.Optional[int] = None)
:canonical: pycityagent.workflow.trigger.TimeTrigger

Bases: {py:obj}`pycityagent.workflow.trigger.EventTrigger`

```{autodoc2-docstring} pycityagent.workflow.trigger.TimeTrigger
```

```{rubric} Initialization
```

```{autodoc2-docstring} pycityagent.workflow.trigger.TimeTrigger.__init__
```

````{py:attribute} required_components
:canonical: pycityagent.workflow.trigger.TimeTrigger.required_components
:value: >
   None

```{autodoc2-docstring} pycityagent.workflow.trigger.TimeTrigger.required_components
```

````

````{py:method} initialize() -> None
:canonical: pycityagent.workflow.trigger.TimeTrigger.initialize

```{autodoc2-docstring} pycityagent.workflow.trigger.TimeTrigger.initialize
```

````

````{py:method} _monitor_time()
:canonical: pycityagent.workflow.trigger.TimeTrigger._monitor_time
:async:

```{autodoc2-docstring} pycityagent.workflow.trigger.TimeTrigger._monitor_time
```

````

````{py:method} wait_for_trigger() -> None
:canonical: pycityagent.workflow.trigger.TimeTrigger.wait_for_trigger
:async:

```{autodoc2-docstring} pycityagent.workflow.trigger.TimeTrigger.wait_for_trigger
```

````

`````
