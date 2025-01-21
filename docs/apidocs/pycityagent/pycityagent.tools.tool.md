# {py:mod}`pycityagent.tools.tool`

```{py:module} pycityagent.tools.tool
```

```{autodoc2-docstring} pycityagent.tools.tool
:allowtitles:
```

## Module Contents

### Classes

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`Tool <pycityagent.tools.tool.Tool>`
  - ```{autodoc2-docstring} pycityagent.tools.tool.Tool
    :summary:
    ```
* - {py:obj}`GetMap <pycityagent.tools.tool.GetMap>`
  - ```{autodoc2-docstring} pycityagent.tools.tool.GetMap
    :summary:
    ```
* - {py:obj}`SencePOI <pycityagent.tools.tool.SencePOI>`
  - ```{autodoc2-docstring} pycityagent.tools.tool.SencePOI
    :summary:
    ```
* - {py:obj}`UpdateWithSimulator <pycityagent.tools.tool.UpdateWithSimulator>`
  -
* - {py:obj}`ResetAgentPosition <pycityagent.tools.tool.ResetAgentPosition>`
  -
* - {py:obj}`ExportMlflowMetrics <pycityagent.tools.tool.ExportMlflowMetrics>`
  -
````

### API

`````{py:class} Tool
:canonical: pycityagent.tools.tool.Tool

```{autodoc2-docstring} pycityagent.tools.tool.Tool
```

````{py:method} __get__(instance, owner)
:canonical: pycityagent.tools.tool.Tool.__get__

```{autodoc2-docstring} pycityagent.tools.tool.Tool.__get__
```

````

````{py:method} __call__(*args: typing.Any, **kwds: typing.Any) -> typing.Any
:canonical: pycityagent.tools.tool.Tool.__call__
:abstractmethod:

```{autodoc2-docstring} pycityagent.tools.tool.Tool.__call__
```

````

````{py:property} agent
:canonical: pycityagent.tools.tool.Tool.agent
:type: pycityagent.agent.Agent

```{autodoc2-docstring} pycityagent.tools.tool.Tool.agent
```

````

````{py:property} block
:canonical: pycityagent.tools.tool.Tool.block
:type: pycityagent.workflow.Block

```{autodoc2-docstring} pycityagent.tools.tool.Tool.block
```

````

`````

`````{py:class} GetMap()
:canonical: pycityagent.tools.tool.GetMap

Bases: {py:obj}`pycityagent.tools.tool.Tool`

```{autodoc2-docstring} pycityagent.tools.tool.GetMap
```

```{rubric} Initialization
```

```{autodoc2-docstring} pycityagent.tools.tool.GetMap.__init__
```

````{py:method} __call__() -> typing.Union[typing.Any, collections.abc.Callable]
:canonical: pycityagent.tools.tool.GetMap.__call__
:async:

```{autodoc2-docstring} pycityagent.tools.tool.GetMap.__call__
```

````

`````

`````{py:class} SencePOI(radius: int = 100, category_prefix=LEVEL_ONE_PRE)
:canonical: pycityagent.tools.tool.SencePOI

Bases: {py:obj}`pycityagent.tools.tool.Tool`

```{autodoc2-docstring} pycityagent.tools.tool.SencePOI
```

```{rubric} Initialization
```

```{autodoc2-docstring} pycityagent.tools.tool.SencePOI.__init__
```

````{py:method} __call__(radius: typing.Optional[int] = None, category_prefix: typing.Optional[str] = None) -> typing.Union[typing.Any, collections.abc.Callable]
:canonical: pycityagent.tools.tool.SencePOI.__call__
:async:

```{autodoc2-docstring} pycityagent.tools.tool.SencePOI.__call__
```

````

`````

`````{py:class} UpdateWithSimulator()
:canonical: pycityagent.tools.tool.UpdateWithSimulator

Bases: {py:obj}`pycityagent.tools.tool.Tool`

````{py:method} _update_motion_with_sim()
:canonical: pycityagent.tools.tool.UpdateWithSimulator._update_motion_with_sim
:async:

```{autodoc2-docstring} pycityagent.tools.tool.UpdateWithSimulator._update_motion_with_sim
```

````

````{py:method} __call__()
:canonical: pycityagent.tools.tool.UpdateWithSimulator.__call__
:async:

```{autodoc2-docstring} pycityagent.tools.tool.UpdateWithSimulator.__call__
```

````

`````

`````{py:class} ResetAgentPosition()
:canonical: pycityagent.tools.tool.ResetAgentPosition

Bases: {py:obj}`pycityagent.tools.tool.Tool`

````{py:method} __call__(aoi_id: typing.Optional[int] = None, poi_id: typing.Optional[int] = None, lane_id: typing.Optional[int] = None, s: typing.Optional[float] = None)
:canonical: pycityagent.tools.tool.ResetAgentPosition.__call__
:async:

```{autodoc2-docstring} pycityagent.tools.tool.ResetAgentPosition.__call__
```

````

`````

`````{py:class} ExportMlflowMetrics(log_batch_size: int = 100)
:canonical: pycityagent.tools.tool.ExportMlflowMetrics

Bases: {py:obj}`pycityagent.tools.tool.Tool`

````{py:method} __call__(metric: typing.Union[collections.abc.Sequence[typing.Union[mlflow.entities.Metric, dict]], typing.Union[mlflow.entities.Metric, dict]], clear_cache: bool = False)
:canonical: pycityagent.tools.tool.ExportMlflowMetrics.__call__
:async:

```{autodoc2-docstring} pycityagent.tools.tool.ExportMlflowMetrics.__call__
```

````

````{py:method} _clear_cache()
:canonical: pycityagent.tools.tool.ExportMlflowMetrics._clear_cache
:async:

```{autodoc2-docstring} pycityagent.tools.tool.ExportMlflowMetrics._clear_cache
```

````

`````
