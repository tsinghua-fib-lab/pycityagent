import asyncio
import time
from collections import defaultdict
from collections.abc import Callable, Sequence
from typing import Any, Optional, Union

from mlflow.entities import Metric

from ..agent import Agent
from ..environment import (LEVEL_ONE_PRE, POI_TYPE_DICT, AoiService,
                           PersonService)
from ..utils.decorators import lock_decorator
from ..workflow import Block


class Tool:
    """Abstract tool class for callable tools. Can be bound to an `Agent` or `Block` instance.

    This class serves as a base for creating various tools that can perform different operations.
    It is intended to be subclassed by specific tool implementations.
    """

    def __get__(self, instance, owner):
        if instance is None:
            return self
        subclass = type(self)
        if not hasattr(instance, "_tools"):
            instance._tools = {}
        if subclass not in instance._tools:
            tool_instance = subclass()
            tool_instance._instance = instance  # type: ignore
            instance._tools[subclass] = tool_instance
        return instance._tools[subclass]

    def __call__(self, *args: Any, **kwds: Any) -> Any:
        """Invoke the tool's functionality.

        This method must be implemented by subclasses to provide specific behavior.
        """
        raise NotImplementedError

    @property
    def agent(self) -> Agent:
        instance = self._instance  # type:ignore
        if not isinstance(instance, Agent):
            raise RuntimeError(
                f"Tool bind to object `{type(instance).__name__}`, not an `Agent` object!"
            )
        return instance

    @property
    def block(self) -> Block:
        instance = self._instance  # type:ignore
        if not isinstance(instance, Block):
            raise RuntimeError(
                f"Tool bind to object `{type(instance).__name__}`, not an `Block` object!"
            )
        return instance


class GetMap(Tool):
    """Retrieve the map from the simulator. Can be bound only to an `Agent` instance."""

    def __init__(self) -> None:
        self.variables = []

    async def __call__(self) -> Union[Any, Callable]:
        agent = self.agent
        if agent.simulator is None:
            raise ValueError("Simulator is not set.")
        return agent.simulator.map


class SencePOI(Tool):
    """Retrieve the Point of Interest (POI) of the current scene.

    This tool computes the POI based on the current `position` stored in memory and returns
    points of interest (POIs) within a specified radius. Can be bound only to an `Agent` instance.

    Attributes:
        radius (int): The radius within which to search for POIs.
        category_prefix (str): The prefix for the categories of POIs to consider.
        variables (list[str]): A list of variables relevant to the tool's operation.

    Args:
        radius (int, optional): The circular search radius. Defaults to 100.
        category_prefix (str, optional): The category prefix to filter POIs. Defaults to LEVEL_ONE_PRE.

    Methods:
        __call__(radius: Optional[int] = None, category_prefix: Optional[str] = None) -> Union[Any, Callable]:
            Executes the AOI retrieval operation, returning POIs based on the current state of memory and simulator.
    """

    def __init__(self, radius: int = 100, category_prefix=LEVEL_ONE_PRE) -> None:
        self.radius = radius
        self.category_prefix = category_prefix
        self.variables = ["position"]

    async def __call__(
        self, radius: Optional[int] = None, category_prefix: Optional[str] = None
    ) -> Union[Any, Callable]:
        """Retrieve the POIs within the specified radius and category prefix.

        If both `radius` and `category_prefix` are None, the method will use the current position
        from memory to query POIs using the simulator. Otherwise, it will return a new instance
        of SenceAoi with the specified parameters.

        Args:
            radius (Optional[int]): A specific radius for the AOI query. If not provided, defaults to the instance's radius.
            category_prefix (Optional[str]): A specific category prefix to filter POIs. If not provided, defaults to the instance's category_prefix.

        Raises:
            ValueError: If memory or simulator is not set.

        Returns:
            Union[Any, Callable]: The query results or a callable for a new SenceAoi instance.
        """
        agent = self.agent
        if agent.memory is None or agent.simulator is None:
            raise ValueError("Memory or Simulator is not set.")
        if radius is None and category_prefix is None:
            position = await agent.status.get("position")
            resp = []
            for prefix in self.category_prefix:
                resp += agent.simulator.map.query_pois(
                    center=(position["xy_position"]["x"], position["xy_position"]["y"]),
                    radius=self.radius,
                    category_prefix=prefix,
                )
            # * Map six-digit codes to specific types
            for poi in resp:
                cate_str = poi[0]["category"]
                poi[0]["category"] = POI_TYPE_DICT[cate_str]
        else:
            radius_ = radius if radius else self.radius
            return SencePOI(radius_, category_prefix)


class UpdateWithSimulator(Tool):
    def __init__(self) -> None:
        self._lock = asyncio.Lock()

    async def _update_motion_with_sim(
        self,
    ):
        agent = self.agent
        if agent._simulator is None:
            return
        simulator = agent.simulator
        status = agent.status
        person_id = await status.get("id")
        resp = await simulator.get_person(person_id)
        resp_dict = resp["person"]
        for k, v in resp_dict.get("motion", {}).items():
            try:
                await status.get(k)
                await status.update(
                    k, v, mode="replace", protect_llm_read_only_fields=False
                )
            except KeyError as e:
                continue

    @lock_decorator
    async def __call__(
        self,
    ):
        agent = self.agent
        await self._update_motion_with_sim()


class ResetAgentPosition(Tool):
    def __init__(self) -> None:
        self._lock = asyncio.Lock()

    @lock_decorator
    async def __call__(
        self,
        aoi_id: Optional[int] = None,
        poi_id: Optional[int] = None,
        lane_id: Optional[int] = None,
        s: Optional[float] = None,
    ):
        agent = self.agent
        status = agent.status
        await agent.simulator.reset_person_position(
            person_id=await status.get("id"),
            aoi_id=aoi_id,
            poi_id=poi_id,
            lane_id=lane_id,
            s=s,
        )


class ExportMlflowMetrics(Tool):
    def __init__(self, log_batch_size: int = 100) -> None:
        self._log_batch_size = log_batch_size
        # TODO: support other log types
        self.metric_log_cache: dict[str, list[Metric]] = defaultdict(list)
        self._lock = asyncio.Lock()

    @lock_decorator
    async def __call__(
        self,
        metric: Union[Sequence[Union[Metric, dict]], Union[Metric, dict]],
        clear_cache: bool = False,
    ):
        agent = self.agent
        batch_size = self._log_batch_size
        if not isinstance(metric, Sequence):
            metric = [metric]
        for _metric in metric:
            if isinstance(_metric, Metric):
                item = _metric
                metric_key = item.key
            else:
                item = Metric(
                    key=_metric["key"],
                    value=_metric["value"],
                    timestamp=_metric.get("timestamp", int(1000 * time.time())),
                    step=_metric["step"],
                )
                metric_key = _metric["key"]
            self.metric_log_cache[metric_key].append(item)
        for metric_key, _cache in self.metric_log_cache.items():
            if len(_cache) > batch_size:
                client = agent.mlflow_client
                await client.log_batch(
                    metrics=_cache[:batch_size],
                )
                _cache = _cache[batch_size:]
        if clear_cache:
            await self._clear_cache()

    async def _clear_cache(
        self,
    ):
        agent = self.agent
        client = agent.mlflow_client
        for metric_key, _cache in self.metric_log_cache.items():
            if len(_cache) > 0:
                await client.log_batch(
                    metrics=_cache,
                )
                _cache = []
