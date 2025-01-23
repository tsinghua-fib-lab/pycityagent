# MLflow Integration

We provide tool to easily export your experiment to the MLflow platform for visualization.

## 1. Initialize Connection
```python
def init_mlflow_connection(config: dict, experiment_uuid: str) -> tuple:
    """
    Initialize MLflow tracking connection
    
    Args:
        config: {
            "username": str,
            "password": str,
            "mlflow_uri": str
        }
        experiment_uuid: Unique experiment identifier
    
    Returns:
        tuple: (run_id, (mlflow_uri, client, run, run_uuid))
    """
```

## 2. MlflowClient Class
```python
class MlflowClient:
    async def log_metric(
        self,
        key: str,
        value: float,
        step: Optional[int] = None,
        timestamp: Optional[int] = None
    ) -> None:
        """Log numerical metrics"""
        
    async def log_metrics(
        self,
        metrics: dict[str, float],
        step: Optional[int] = None
    ) -> None:
        """Log multiple metrics at once"""
```

## 3. Usage

Provide Mlflow argument in your config file.

```yaml
metric_request:
  mlflow: 
    username: <USER-NAME>
    password: <PASSWORD>
    mlflow_uri: <MLFLOW-URI>
```

```python
import asyncio
import random

from pycityagent.agent import Agent, CitizenAgent
from pycityagent.metrics import MlflowClient, init_mlflow_connection
from pycityagent.tools import ExportMlflowMetrics

class MlflowTestAgent(CitizenAgent):
    export_metrics = ExportMlflowMetrics(log_batch_size=10)

    def __init__(
        self,
        name: str,
        mlfow_client: MlflowClient,
    ) -> None:
        super().__init__(
            name,
        )
        self._step = -1

    # Main workflow
    async def forward(self):
        self._step += 1
        if self._step <= 100:
            await self.export_metrics(
                metric={
                    "key": f"metric_{self._agent_id}",
                    "value": self._step + random.random(),
                    "step": self._step,
                },
                clear_cache=self._step >= 100,
            )

async def main():
    mlflow_config = {
        "username": "",
        "password": "",
        "mlflow_uri": "<MLFLOW-URI>",
    }
    exp_name = "test"
    experiment_uuid = "123"
    run_id, (uri, client, run, run_uuid) = init_mlflow_connection(
        config=mlflow_config,
        experiment_uuid=experiment_uuid,
    )
    mlflow_client = MlflowClient(
        config=mlflow_config,
        experiment_uuid=experiment_uuid,
        mlflow_run_name=f"{exp_name}_{run_uuid}",
        experiment_name=exp_name,
        run_id=run_id,
    )
    agent = MlflowTestAgent("test", mlflow_client)
    for _ in range(100):
        await agent.forward()


if __name__ == "__main__":
    asyncio.run(main())

```
