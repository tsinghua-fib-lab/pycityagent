import asyncio
import logging
from copy import deepcopy
from typing import Any, Callable, Dict, List, Optional, Union

from mosstool.util.format_converter import dict2pb
from pycityproto.city.person.v2 import person_pb2 as person_pb2

from ..agent import Agent
from ..environment import (LEVEL_ONE_PRE, POI_TYPE_DICT, AoiService,
                           PersonService)
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
        variables (List[str]): A list of variables relevant to the tool's operation.

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
            position = await agent.memory.get("position")
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
    def __init__(
        self,
        person_template_func: Callable[[], dict] = PersonService.default_dict_person,
    ) -> None:
        self.person_template_func = person_template_func

    async def _bind_to_simulator(
        self,
    ):
        """
        Bind Agent to Simulator

        Args:
            person_template (dict, optional): The person template in dict format. Defaults to PersonService.default_dict_person().
        """
        agent = self.agent
        if agent._simulator is None:
            return
        if not agent._has_bound_to_simulator:
            FROM_MEMORY_KEYS = {
                "attribute",
                "home",
                "work",
                "vehicle_attribute",
                "bus_attribute",
                "pedestrian_attribute",
                "bike_attribute",
            }
            simulator = agent.simulator
            memory = agent.memory
            person_id = await memory.get("id")
            # ATTENTION:模拟器分配的id从0开始
            if person_id >= 0:
                await simulator.GetPerson(person_id)
                logging.debug(f"Binding to Person `{person_id}` already in Simulator")
            else:
                dict_person = deepcopy(self.person_template_func())
                for _key in FROM_MEMORY_KEYS:
                    try:
                        _value = await memory.get(_key)
                        if _value:
                            dict_person[_key] = _value
                    except KeyError as e:
                        continue
                resp = await simulator.AddPerson(
                    dict2pb(dict_person, person_pb2.Person())
                )
                person_id = resp["person_id"]
                await memory.update("id", person_id, protect_llm_read_only_fields=False)
                logging.debug(
                    f"Binding to Person `{person_id}` just added to Simulator"
                )
                # 防止模拟器还没有到prepare阶段导致GetPerson出错
                await asyncio.sleep(5)
            agent._has_bound_to_simulator = True
        else:
            pass

    async def _update_motion_with_sim(
        self,
    ):
        agent = self.agent
        if agent._simulator is None:
            return
        if not agent._has_bound_to_simulator:
            await self._bind_to_simulator()
        simulator = agent.simulator
        memory = agent.memory
        person_id = await memory.get("id")
        resp = await simulator.GetPerson(person_id)
        resp_dict = resp["person"]
        for k, v in resp_dict.get("motion", {}).items():
            try:
                await memory.get(k)
                await memory.update(
                    k, v, mode="replace", protect_llm_read_only_fields=False
                )
            except KeyError as e:
                continue

    async def __call__(
        self,
    ):
        agent = self.agent
        await self._bind_to_simulator()
        await self._update_motion_with_sim()


class ResetAgentPosition(Tool):
    def __init__(self) -> None:
        pass

    async def __call__(
        self,
        aoi_id: Optional[int] = None,
        poi_id: Optional[int] = None,
        lane_id: Optional[int] = None,
        s: Optional[float] = None,
    ):
        agent = self.agent
        memory = agent.memory
        await agent.simulator.ResetPersonPosition(
            person_id=await memory.get("id"),
            aoi_id=aoi_id,
            poi_id=poi_id,
            lane_id=lane_id,
            s=s,
        )
