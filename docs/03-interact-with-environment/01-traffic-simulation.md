# City Simulator

The City Simulator serves as the mobility simulation playground for agents within the framework.

## Constructor
```python

class Simulator:

    def __init__(self, config: dict, secure: bool = False) -> None:
    """
    Parameters:
        config: the configuration dict
        secure: whether use secure connection for grpc APIs.
    """
```

### Configuration Structure
```python
simulator_config:
  map_request:
    mongo_uri: "mongodb://localhost:27017"
    mongo_db: "srt"
    mongo_coll: "map_beijing_extend_20241201"
    cache_dir: "./cache"
```

## Key Methods

### Environment Control Methods
```python

    async def pause(self) -> None:
        """Pause simulation execution"""

    async def resume(self) -> None:
        """Resume simulation execution"""

    def set_environment(self, environment: dict[str, str]):
        """
        Set the entire dictionary of environment variables.
        """

    def update_environment(self, key: str, value: str):
        """
        Update the value of a single environment variable.
        """
```

### Agent Management Methods
```python
    async def add_person(self, person: person_pb2.Person | dict) -> dict:
        """
        Add new person to simulation
        
        Args:
            person (Any): The person object to add. If it's an instance of `person_pb2.Person`, it will be wrapped in an `AddPersonRequest`. Otherwise, `person` is expected to already be a valid request object.
            
        Returns:
            dict: {"person_id": str} Person identifier
        """

    async def set_aoi_schedules(
        self,
        person_id: int,
        target_positions: Union[
            list[Union[int, tuple[int, int]]], Union[int, tuple[int, int]]
        ],
        departure_times: Optional[list[float]] = None,
        modes: Optional[list[TripMode]] = None,
    ):
        """
        Set schedules for a person to visit Areas of Interest (AOIs).
        """

    async def reset_person_position(
        self,
        person_id: int,
        aoi_id: Optional[int] = None,
        poi_id: Optional[int] = None,
        lane_id: Optional[int] = None,
        s: Optional[float] = None,
    ):
        """
        Reset the position of a person within the simulation.
        """

    async def get_person(self, person_id: int) -> dict:
        """
        Retrieve information about a specific person by ID.
        """
```

### Map and Location Methods
```python
    def get_poi_categories(
        self,
        center: Optional[Union[tuple[float, float], Point]] = None,
        radius: Optional[float] = None,
    ) -> list[str]:
        """
        Retrieve unique categories of Points of Interest (POIs) around a central point.
        """

    def get_around_poi(
        self,
        center: Union[tuple[float, float], Point],
        radius: float,
        poi_type: Union[str, list[str]],
    ) -> list[dict]:
        """
        Get Points of Interest (POIs) around a central point based on type.
        """
```

### Time Management Methods
```python
    async def get_time(
        self, format_time: bool = False, format: str = "%H:%M:%S"
    ) -> Union[int, str]:
        """
        Get the current time of the simulator.

        By default, returns the number of seconds since midnight. Supports formatted output.

        """

    async def set_time_scale(self, scale: float) -> None:
        """
        Set simulation time scale
        
        Args:
            scale (float): Time progression multiplier
        """
```
