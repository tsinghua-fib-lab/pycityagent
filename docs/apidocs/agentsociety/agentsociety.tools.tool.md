# {py:mod}`agentsociety.tools.tool`

```{py:module} agentsociety.tools.tool
```

```{autodoc2-docstring} agentsociety.tools.tool
:allowtitles:
```

## Module Contents

### Classes

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`Tool <agentsociety.tools.tool.Tool>`
  - ```{autodoc2-docstring} agentsociety.tools.tool.Tool
    :summary:
    ```
* - {py:obj}`GetMap <agentsociety.tools.tool.GetMap>`
  - ```{autodoc2-docstring} agentsociety.tools.tool.GetMap
    :summary:
    ```
* - {py:obj}`UpdateWithSimulator <agentsociety.tools.tool.UpdateWithSimulator>`
  - ```{autodoc2-docstring} agentsociety.tools.tool.UpdateWithSimulator
    :summary:
    ```
* - {py:obj}`ResetAgentPosition <agentsociety.tools.tool.ResetAgentPosition>`
  -
* - {py:obj}`ExportMlflowMetrics <agentsociety.tools.tool.ExportMlflowMetrics>`
  - ```{autodoc2-docstring} agentsociety.tools.tool.ExportMlflowMetrics
    :summary:
    ```
````

### Data

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`__all__ <agentsociety.tools.tool.__all__>`
  - ```{autodoc2-docstring} agentsociety.tools.tool.__all__
    :summary:
    ```
````

### API

````{py:data} __all__
:canonical: agentsociety.tools.tool.__all__
:value: >
   ['Tool', 'ExportMlflowMetrics', 'GetMap', 'UpdateWithSimulator', 'ResetAgentPosition']

```{autodoc2-docstring} agentsociety.tools.tool.__all__
```

````

`````{py:class} Tool
:canonical: agentsociety.tools.tool.Tool

```{autodoc2-docstring} agentsociety.tools.tool.Tool
```

````{py:method} __get__(instance, owner)
:canonical: agentsociety.tools.tool.Tool.__get__

```{autodoc2-docstring} agentsociety.tools.tool.Tool.__get__
```

````

````{py:method} __call__(*args: typing.Any, **kwds: typing.Any) -> typing.Any
:canonical: agentsociety.tools.tool.Tool.__call__
:abstractmethod:

```{autodoc2-docstring} agentsociety.tools.tool.Tool.__call__
```

````

````{py:property} agent
:canonical: agentsociety.tools.tool.Tool.agent
:type: agentsociety.agent.Agent

```{autodoc2-docstring} agentsociety.tools.tool.Tool.agent
```

````

````{py:property} block
:canonical: agentsociety.tools.tool.Tool.block
:type: agentsociety.workflow.Block

```{autodoc2-docstring} agentsociety.tools.tool.Tool.block
```

````

`````

`````{py:class} GetMap()
:canonical: agentsociety.tools.tool.GetMap

Bases: {py:obj}`agentsociety.tools.tool.Tool`

```{autodoc2-docstring} agentsociety.tools.tool.GetMap
```

```{rubric} Initialization
```

```{autodoc2-docstring} agentsociety.tools.tool.GetMap.__init__
```

````{py:method} __call__() -> typing.Union[typing.Any, collections.abc.Callable]
:canonical: agentsociety.tools.tool.GetMap.__call__
:async:

```{autodoc2-docstring} agentsociety.tools.tool.GetMap.__call__
```

````

`````

`````{py:class} UpdateWithSimulator()
:canonical: agentsociety.tools.tool.UpdateWithSimulator

Bases: {py:obj}`agentsociety.tools.tool.Tool`

```{autodoc2-docstring} agentsociety.tools.tool.UpdateWithSimulator
```

```{rubric} Initialization
```

```{autodoc2-docstring} agentsociety.tools.tool.UpdateWithSimulator.__init__
```

````{py:method} _update_motion_with_sim()
:canonical: agentsociety.tools.tool.UpdateWithSimulator._update_motion_with_sim
:async:

```{autodoc2-docstring} agentsociety.tools.tool.UpdateWithSimulator._update_motion_with_sim
```

````

````{py:method} __call__()
:canonical: agentsociety.tools.tool.UpdateWithSimulator.__call__
:async:

```{autodoc2-docstring} agentsociety.tools.tool.UpdateWithSimulator.__call__
```

````

`````

`````{py:class} ResetAgentPosition()
:canonical: agentsociety.tools.tool.ResetAgentPosition

Bases: {py:obj}`agentsociety.tools.tool.Tool`

````{py:method} __call__(aoi_id: typing.Optional[int] = None, poi_id: typing.Optional[int] = None, lane_id: typing.Optional[int] = None, s: typing.Optional[float] = None)
:canonical: agentsociety.tools.tool.ResetAgentPosition.__call__
:async:

```{autodoc2-docstring} agentsociety.tools.tool.ResetAgentPosition.__call__
```

````

`````

`````{py:class} ExportMlflowMetrics(log_batch_size: int = 100)
:canonical: agentsociety.tools.tool.ExportMlflowMetrics

Bases: {py:obj}`agentsociety.tools.tool.Tool`

```{autodoc2-docstring} agentsociety.tools.tool.ExportMlflowMetrics
```

```{rubric} Initialization
```

```{autodoc2-docstring} agentsociety.tools.tool.ExportMlflowMetrics.__init__
```

````{py:method} __call__(metric: typing.Union[collections.abc.Sequence[typing.Union[mlflow.entities.Metric, dict]], typing.Union[mlflow.entities.Metric, dict]], clear_cache: bool = False)
:canonical: agentsociety.tools.tool.ExportMlflowMetrics.__call__
:async:

```{autodoc2-docstring} agentsociety.tools.tool.ExportMlflowMetrics.__call__
```

````

````{py:method} _clear_cache()
:canonical: agentsociety.tools.tool.ExportMlflowMetrics._clear_cache
:async:

```{autodoc2-docstring} agentsociety.tools.tool.ExportMlflowMetrics._clear_cache
```

````

`````
