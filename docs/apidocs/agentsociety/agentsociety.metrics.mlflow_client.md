# {py:mod}`agentsociety.metrics.mlflow_client`

```{py:module} agentsociety.metrics.mlflow_client
```

```{autodoc2-docstring} agentsociety.metrics.mlflow_client
:allowtitles:
```

## Module Contents

### Classes

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`MlflowClient <agentsociety.metrics.mlflow_client.MlflowClient>`
  - ```{autodoc2-docstring} agentsociety.metrics.mlflow_client.MlflowClient
    :summary:
    ```
````

### Functions

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`init_mlflow_connection <agentsociety.metrics.mlflow_client.init_mlflow_connection>`
  - ```{autodoc2-docstring} agentsociety.metrics.mlflow_client.init_mlflow_connection
    :summary:
    ```
````

### Data

````{list-table}
:class: autosummary longtable
:align: left

* - {py:obj}`__all__ <agentsociety.metrics.mlflow_client.__all__>`
  - ```{autodoc2-docstring} agentsociety.metrics.mlflow_client.__all__
    :summary:
    ```
* - {py:obj}`logger <agentsociety.metrics.mlflow_client.logger>`
  - ```{autodoc2-docstring} agentsociety.metrics.mlflow_client.logger
    :summary:
    ```
````

### API

````{py:data} __all__
:canonical: agentsociety.metrics.mlflow_client.__all__
:value: >
   ['init_mlflow_connection', 'MlflowClient']

```{autodoc2-docstring} agentsociety.metrics.mlflow_client.__all__
```

````

````{py:data} logger
:canonical: agentsociety.metrics.mlflow_client.logger
:value: >
   'getLogger(...)'

```{autodoc2-docstring} agentsociety.metrics.mlflow_client.logger
```

````

````{py:function} init_mlflow_connection(config: agentsociety.configs.MlflowConfig, experiment_uuid: str, mlflow_run_name: typing.Optional[str] = None, experiment_name: typing.Optional[str] = None, experiment_description: typing.Optional[str] = None, experiment_tags: typing.Optional[dict[str, typing.Any]] = None) -> tuple[str, tuple[str, mlflow.MlflowClient, mlflow.entities.Run, str]]
:canonical: agentsociety.metrics.mlflow_client.init_mlflow_connection

```{autodoc2-docstring} agentsociety.metrics.mlflow_client.init_mlflow_connection
```
````

`````{py:class} MlflowClient(config: agentsociety.configs.MlflowConfig, experiment_uuid: str, mlflow_run_name: typing.Optional[str] = None, experiment_name: typing.Optional[str] = None, experiment_description: typing.Optional[str] = None, experiment_tags: typing.Optional[dict[str, typing.Any]] = None, run_id: typing.Optional[str] = None)
:canonical: agentsociety.metrics.mlflow_client.MlflowClient

```{autodoc2-docstring} agentsociety.metrics.mlflow_client.MlflowClient
```

```{rubric} Initialization
```

```{autodoc2-docstring} agentsociety.metrics.mlflow_client.MlflowClient.__init__
```

````{py:property} client
:canonical: agentsociety.metrics.mlflow_client.MlflowClient.client
:type: mlflow.MlflowClient

```{autodoc2-docstring} agentsociety.metrics.mlflow_client.MlflowClient.client
```

````

````{py:property} run_id
:canonical: agentsociety.metrics.mlflow_client.MlflowClient.run_id
:type: str

```{autodoc2-docstring} agentsociety.metrics.mlflow_client.MlflowClient.run_id
```

````

````{py:method} log_batch(metrics: collections.abc.Sequence[mlflow.entities.Metric] = (), params: collections.abc.Sequence[mlflow.entities.Param] = (), tags: collections.abc.Sequence[mlflow.entities.RunTag] = ())
:canonical: agentsociety.metrics.mlflow_client.MlflowClient.log_batch
:async:

```{autodoc2-docstring} agentsociety.metrics.mlflow_client.MlflowClient.log_batch
```

````

````{py:method} log_metric(key: str, value: float, step: typing.Optional[int] = None, timestamp: typing.Optional[int] = None)
:canonical: agentsociety.metrics.mlflow_client.MlflowClient.log_metric
:async:

```{autodoc2-docstring} agentsociety.metrics.mlflow_client.MlflowClient.log_metric
```

````

`````
