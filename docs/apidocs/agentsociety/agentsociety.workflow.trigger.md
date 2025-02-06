# {py:mod}`agentsociety.workflow.trigger`

```{py:module} agentsociety.workflow.trigger
```

```{autodoc2-docstring} agentsociety.workflow.trigger
:allowtitles:
```

## Module Contents

### Classes

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`EventTrigger <agentsociety.workflow.trigger.EventTrigger>`
  - ```{autodoc2-docstring} agentsociety.workflow.trigger.EventTrigger
    :summary:
    ```
* - {py:obj}`MemoryChangeTrigger <agentsociety.workflow.trigger.MemoryChangeTrigger>`
  - ```{autodoc2-docstring} agentsociety.workflow.trigger.MemoryChangeTrigger
    :summary:
    ```
* - {py:obj}`TimeTrigger <agentsociety.workflow.trigger.TimeTrigger>`
  - ```{autodoc2-docstring} agentsociety.workflow.trigger.TimeTrigger
    :summary:
    ```
````

### Data

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`KEY_TRIGGER_COMPONENTS <agentsociety.workflow.trigger.KEY_TRIGGER_COMPONENTS>`
  - ```{autodoc2-docstring} agentsociety.workflow.trigger.KEY_TRIGGER_COMPONENTS
    :summary:
    ```
* - {py:obj}`__all__ <agentsociety.workflow.trigger.__all__>`
  - ```{autodoc2-docstring} agentsociety.workflow.trigger.__all__
    :summary:
    ```
````

### API

````{py:data} KEY_TRIGGER_COMPONENTS
:canonical: agentsociety.workflow.trigger.KEY_TRIGGER_COMPONENTS
:value: >
   None

```{autodoc2-docstring} agentsociety.workflow.trigger.KEY_TRIGGER_COMPONENTS
```

````

````{py:data} __all__
:canonical: agentsociety.workflow.trigger.__all__
:value: >
   ['EventTrigger', 'MemoryChangeTrigger', 'TimeTrigger']

```{autodoc2-docstring} agentsociety.workflow.trigger.__all__
```

````

`````{py:class} EventTrigger(block=None)
:canonical: agentsociety.workflow.trigger.EventTrigger

```{autodoc2-docstring} agentsociety.workflow.trigger.EventTrigger
```

```{rubric} Initialization
```

```{autodoc2-docstring} agentsociety.workflow.trigger.EventTrigger.__init__
```

````{py:attribute} required_components
:canonical: agentsociety.workflow.trigger.EventTrigger.required_components
:type: list[type]
:value: >
   []

```{autodoc2-docstring} agentsociety.workflow.trigger.EventTrigger.required_components
```

````

````{py:method} initialize() -> None
:canonical: agentsociety.workflow.trigger.EventTrigger.initialize

```{autodoc2-docstring} agentsociety.workflow.trigger.EventTrigger.initialize
```

````

````{py:method} wait_for_trigger() -> None
:canonical: agentsociety.workflow.trigger.EventTrigger.wait_for_trigger
:abstractmethod:
:async:

```{autodoc2-docstring} agentsociety.workflow.trigger.EventTrigger.wait_for_trigger
```

````

`````

`````{py:class} MemoryChangeTrigger(key: str)
:canonical: agentsociety.workflow.trigger.MemoryChangeTrigger

Bases: {py:obj}`agentsociety.workflow.trigger.EventTrigger`

```{autodoc2-docstring} agentsociety.workflow.trigger.MemoryChangeTrigger
```

```{rubric} Initialization
```

```{autodoc2-docstring} agentsociety.workflow.trigger.MemoryChangeTrigger.__init__
```

````{py:attribute} required_components
:canonical: agentsociety.workflow.trigger.MemoryChangeTrigger.required_components
:value: >
   None

```{autodoc2-docstring} agentsociety.workflow.trigger.MemoryChangeTrigger.required_components
```

````

````{py:method} initialize() -> None
:canonical: agentsociety.workflow.trigger.MemoryChangeTrigger.initialize

```{autodoc2-docstring} agentsociety.workflow.trigger.MemoryChangeTrigger.initialize
```

````

````{py:method} wait_for_trigger() -> None
:canonical: agentsociety.workflow.trigger.MemoryChangeTrigger.wait_for_trigger
:async:

```{autodoc2-docstring} agentsociety.workflow.trigger.MemoryChangeTrigger.wait_for_trigger
```

````

`````

`````{py:class} TimeTrigger(days: typing.Optional[int] = None, hours: typing.Optional[int] = None, minutes: typing.Optional[int] = None)
:canonical: agentsociety.workflow.trigger.TimeTrigger

Bases: {py:obj}`agentsociety.workflow.trigger.EventTrigger`

```{autodoc2-docstring} agentsociety.workflow.trigger.TimeTrigger
```

```{rubric} Initialization
```

```{autodoc2-docstring} agentsociety.workflow.trigger.TimeTrigger.__init__
```

````{py:attribute} required_components
:canonical: agentsociety.workflow.trigger.TimeTrigger.required_components
:value: >
   None

```{autodoc2-docstring} agentsociety.workflow.trigger.TimeTrigger.required_components
```

````

````{py:method} initialize() -> None
:canonical: agentsociety.workflow.trigger.TimeTrigger.initialize

```{autodoc2-docstring} agentsociety.workflow.trigger.TimeTrigger.initialize
```

````

````{py:method} _monitor_time()
:canonical: agentsociety.workflow.trigger.TimeTrigger._monitor_time
:async:

```{autodoc2-docstring} agentsociety.workflow.trigger.TimeTrigger._monitor_time
```

````

````{py:method} wait_for_trigger() -> None
:canonical: agentsociety.workflow.trigger.TimeTrigger.wait_for_trigger
:async:

```{autodoc2-docstring} agentsociety.workflow.trigger.TimeTrigger.wait_for_trigger
```

````

`````
