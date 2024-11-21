from typing import Any, Callable, Dict, List, Optional, Union
from ..environment import POI_TYPE_DICT, LEVEL_ONE_PRE, Simulator
from ..memory import Memory


class Tool:
    """Abstract tool class for callable tools.

    This class serves as a base for creating various tools that can perform different operations.
    It is intended to be subclassed by specific tool implementations.
    """

    def __init__(self) -> None:
        self.memory: Optional[Memory] = None
        self.simulator: Optional[Simulator] = None

    async def __call__(self) -> Any:
        """Invoke the tool's functionality.

        This method must be implemented by subclasses to provide specific behavior.
        """
        raise NotImplementedError
    
class GetMap(Tool):
    """Retrieve the map from the simulator.
    """
    def __init__(self) -> None:
        self.variables = []
    
    async def __call__(self) -> Union[Any, Callable]:
        if self.simulator is None:
            raise ValueError('Simulator is not set.')
        return self.simulator.map
    
class SencePOI(Tool):
    """Retrieve the Point of Interest (POI) of the current scene.

    This tool computes the POI based on the current `position` stored in memory and returns 
    points of interest (POIs) within a specified radius. 

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
        if self.memory is None or self.simulator is None:
            raise ValueError("Memory or Simulator is not set.")
        if radius is None and category_prefix is None:
            position = await self.memory.get("position")
            resp = []
            for prefix in self.category_prefix:
                resp += self.simulator.map.query_pois(
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
