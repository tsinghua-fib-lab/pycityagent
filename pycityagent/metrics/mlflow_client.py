import asyncio
import logging
import os
import uuid
from collections.abc import Sequence
from typing import Any, Optional, Union

import mlflow
from mlflow.entities import (Dataset, DatasetInput, Document, Experiment,
                             ExperimentTag, FileInfo, InputTag, LifecycleStage,
                             LiveSpan, Metric, NoOpSpan, Param, Run, RunData,
                             RunInfo, RunInputs, RunStatus, RunTag, SourceType,
                             Span, SpanEvent, SpanStatus, SpanStatusCode,
                             SpanType, Trace, TraceData, TraceInfo, ViewType)

from ..utils.decorators import lock_decorator

logger = logging.getLogger("mlflow")


class MlflowClient:
    """
    - Mlflow client
    """

    def __init__(
        self,
        config: dict,
        mlflow_run_name: Optional[str] = None,
        experiment_name: Optional[str] = None,
        experiment_description: Optional[str] = None,
        experiment_tags: Optional[dict[str, Any]] = None,
    ) -> None:
        os.environ["MLFLOW_TRACKING_USERNAME"] = config.get("username", None)
        os.environ["MLFLOW_TRACKING_PASSWORD"] = config.get("password", None)
        self._mlflow_uri = uri = config["mlflow_uri"]
        self._client = client = mlflow.MlflowClient(tracking_uri=uri)
        self._run_uuid = run_uuid = str(uuid.uuid4())
        self._lock = asyncio.Lock()
        # run name
        if mlflow_run_name is None:
            mlflow_run_name = f"exp_{run_uuid}"

        # exp name
        if experiment_name is None:
            experiment_name = f"run_{run_uuid}"

        # tags
        if experiment_tags is None:
            experiment_tags = {}
        if experiment_description is not None:
            experiment_tags["mlflow.note.content"] = experiment_description

        try:
            self._experiment_id = experiment_id = client.create_experiment(
                name=experiment_name,
                tags=experiment_tags,
            )
        except Exception as e:
            experiment = client.get_experiment_by_name(experiment_name)
            if experiment is None:
                raise e
            self._experiment_id = experiment_id = experiment.experiment_id

        self._run = run = client.create_run(
            experiment_id=experiment_id, run_name=mlflow_run_name
        )
        self._run_id = run.info.run_id

    @property
    def client(
        self,
    ) -> mlflow.MlflowClient:
        return self._client

    @property
    def run_id(
        self,
    ) -> str:
        return self._run_id

    @lock_decorator
    async def log_batch(
        self,
        metrics: Sequence[Metric] = (),
        params: Sequence[Param] = (),
        tags: Sequence[RunTag] = (),
    ):
        self.client.log_batch(
            run_id=self.run_id, metrics=metrics, params=params, tags=tags
        )

    @lock_decorator
    async def log_metric(
        self,
        key: str,
        value: float,
        step: Optional[int] = None,
        timestamp: Optional[int] = None,
    ):
        if timestamp is not None:
            timestamp = int(timestamp)
        self.client.log_metric(
            run_id=self.run_id,
            key=key,
            value=value,
            timestamp=timestamp,
            step=step,
        )
