"""Simulator: 城市模拟器类及其定义"""

import asyncio
import logging
import os
from datetime import datetime, timedelta
import time
from typing import Any, Optional, Union, cast

from mosstool.type import TripMode
from mosstool.util.format_converter import coll2pb
from pycitydata.map import Map as SimMap
from pycityproto.city.map.v2 import map_pb2 as map_pb2
from pycityproto.city.person.v2 import person_pb2 as person_pb2
from pycityproto.city.person.v2 import person_service_pb2 as person_service
from pymongo import MongoClient
from shapely.geometry import Point

from .sim import CityClient, ControlSimEnv
from .utils.const import *

logger = logging.getLogger("pycityagent")

__all__ = [
    "Simulator",
]


class Simulator:
    """
    Main class of the simulator.

    - **Description**:
        - This class is the core of the simulator, responsible for initializing and managing the simulation environment.
        - It reads parameters from a configuration dictionary, initializes map data, and starts or connects to a simulation server as needed.
    """

    def __init__(self, config: dict, secure: bool = False) -> None:
        self.config = config
        """
        - 模拟器配置
        - simulator config
        """
        _mongo_uri, _mongo_db, _mongo_coll, _map_cache_dir = (
            config["map_request"]["mongo_uri"],
            config["map_request"]["mongo_db"],
            config["map_request"]["mongo_coll"],
            config["map_request"]["cache_dir"],
        )
        _mongo_client = MongoClient(_mongo_uri)
        os.makedirs(_map_cache_dir, exist_ok=True)
        _map_pb_path = os.path.join(_map_cache_dir, f"{_mongo_db}.{_mongo_coll}.pb")  # type: ignore
        _map_pb = map_pb2.Map()
        if os.path.exists(_map_pb_path):
            with open(_map_pb_path, "rb") as f:
                _map_pb.ParseFromString(f.read())
        else:
            _map_pb = coll2pb(_mongo_client[_mongo_db][_mongo_coll], _map_pb)
            with open(_map_pb_path, "wb") as f:
                f.write(_map_pb.SerializeToString())

        if "simulator" in config:
            if config["simulator"] is None:
                config["simulator"] = {}
            if "server" not in config["simulator"]:
                self._sim_env = sim_env = ControlSimEnv(
                    task_name=config["simulator"].get("task", "citysim"),
                    map_file=_map_pb_path,
                    start_step=config["simulator"].get("start_step", 0),
                    total_step=2147000000,
                    log_dir=config["simulator"].get("log_dir", "./log"),
                    min_step_time=config["simulator"].get("min_step_time", 1000),
                    sim_addr=config["simulator"].get("server", None),
                )
                self.server_addr = sim_env.sim_addr
                config["simulator"]["server"] = self.server_addr
                # using local client
                self._client = CityClient(sim_env.sim_addr, secure=False)
                """
                - 模拟器grpc客户端
                - grpc client of simulator
                """
            else:
                self._client = CityClient(config["simulator"]["server"], secure=False)
                self.server_addr = config["simulator"]["server"]
        else:
            self.server_addr = None
            logger.warning(
                "No simulator config found, no simulator client will be used"
            )
        self.map = SimMap(
            mongo_uri=_mongo_uri,
            mongo_db=_mongo_db,
            mongo_coll=_mongo_coll,
            cache_dir=_map_cache_dir,
        )
        """
        - 模拟器地图对象
        - Simulator map object
        """

        self.time: int = 0
        """
        - 模拟城市当前时间
        - The current time of simulator
        """
        self.poi_cate = POI_CATG_DICT
        self.map_x_gap = None
        self.map_y_gap = None
        self._bbox: tuple[float, float, float, float] = (-1, -1, -1, -1)
        self._lock = asyncio.Lock()
        # poi id dict
        self.poi_id_2_aoi_id: dict[int, int] = {
            poi["id"]: poi["aoi_id"] for _, poi in self.map.pois.items()
        }
        self._environment_prompt:dict[str, str] = {}
        self._log_list = []

    def get_log_list(self):
        return self._log_list
    
    def clear_log_list(self):
        self._log_list = []

    @property
    def environment(self) -> dict[str, str]:
        """
        Get the current state of environment variables.
        """
        return self._environment_prompt

    def set_environment(self, environment: dict[str, str]):
        """
        Set the entire dictionary of environment variables.

        - **Args**:
            - `environment` (`Dict[str, str]`): Key-value pairs of environment variables.
        """
        self._environment_prompt = environment

    def sence(self, key: str) -> str:
        """
        Retrieve the value of an environment variable by its key.

        - **Args**:
            - `key` (`str`): The key of the environment variable.

        - **Returns**:
            - `str`: The value of the corresponding key, or an empty string if not found.
        """
        return self._environment_prompt.get(key, "")

    def update_environment(self, key: str, value: str):
        """
        Update the value of a single environment variable.

        - **Args**:
            - `key` (`str`): The key of the environment variable.
            - `value` (`str`): The new value to set.
        """
        self._environment_prompt[key] = value

    # * Agent相关
    def find_agents_by_area(self, req: dict, status=None):
        """
        Find agents/persons within a specified area.

        - **Args**:
            - `req` (`dict`): A dictionary that describes the area. Refer to
              https://cityproto.sim.fiblab.net/#city.person.1.GetPersonByLongLatBBoxRequest.
            - `status` (`Optional[int]`): An integer representing the status of the agents/persons to filter by.
              If provided, only persons with the given status will be returned.
              Refer to https://cityproto.sim.fiblab.net/#city.agent.v2.Status.

        - **Returns**:
            - The response from the GetPersonByLongLatBBox method, possibly filtered by status.
              Refer to https://cityproto.sim.fiblab.net/#city.person.1.GetPersonByLongLatBBoxResponse.
        """
        start_time = time.time()
        log = {
            "req": "find_agents_by_area",
            "start_time": start_time,
            "consumption": 0
        }
        loop = asyncio.get_event_loop()
        resp = loop.run_until_complete(
            self._client.person_service.GetPersonByLongLatBBox(req=req)
        )
        loop.close()
        if status == None:
            return resp
        else:
            motions = []
            for agent in resp.motions:  # type: ignore
                if agent.status in status:
                    motions.append(agent)
            resp.motions = motions  # type: ignore
            log["consumption"] = time.time() - start_time
            self._log_list.append(log)
            return resp

    def get_poi_categories(
        self,
        center: Optional[Union[tuple[float, float], Point]] = None,
        radius: Optional[float] = None,
    ) -> list[str]:
        """
        Retrieve unique categories of Points of Interest (POIs) around a central point.

        - **Args**:
            - `center` (`Optional[Union[Tuple[float, float], Point]]`): The central point as a tuple or Point object.
              Defaults to (0, 0) if not provided.
            - `radius` (`Optional[float]`): The search radius in meters. If not provided, all POIs are considered.

        - **Returns**:
            - `List[str]`: A list of unique POI category names.
        """
        start_time = time.time()
        log = {
            "req": "get_poi_categories",
            "start_time": start_time,
            "consumption": 0
        }
        categories: list[str] = []
        if center is None:
            center = (0, 0)
        _pois: list[dict] = self.map.query_pois(  # type:ignore
            center=center,
            radius=radius,
            return_distance=False,
        )
        for poi in _pois:
            catg = poi["category"]
            categories.append(catg.split("|")[-1])
        log["consumption"] = time.time() - start_time
        self._log_list.append(log)
        return list(set(categories))

    async def get_time(
        self, format_time: bool = False, format: str = "%H:%M:%S"
    ) -> Union[int, str]:
        """
        Get the current time of the simulator.

        By default, returns the number of seconds since midnight. Supports formatted output.

        - **Args**:
            - `format_time` (`bool`): Whether to return the time in a formatted string. Defaults to `False`.
            - `format` (`str`): The format string for formatting the time. Defaults to "%H:%M:%S".

        - **Returns**:
            - `Union[int, str]`: The current simulation time either as an integer representing seconds since midnight or as a formatted string.
        """
        start_time = time.time()
        log = {
            "req": "get_time",
            "start_time": start_time,
            "consumption": 0
        }
        now = await self._client.clock_service.Now({})
        now = cast(dict[str, int], now)
        self.time = now["t"]
        if format_time:
            current_date = datetime.now().date()
            start_of_day = datetime.combine(current_date, datetime.min.time())
            current_time = start_of_day + timedelta(seconds=now["t"])
            formatted_time = current_time.strftime(format)
            log["consumption"] = time.time() - start_time
            self._log_list.append(log)
            return formatted_time
        else:
            log["consumption"] = time.time() - start_time
            self._log_list.append(log)
            return int(now["t"])

    async def pause(self):
        """
        Pause the simulation.

        This method sends a request to the simulator's pause service to pause the simulation.
        """
        start_time = time.time()
        log = {
            "req": "pause",
            "start_time": start_time,
            "consumption": 0
        }
        await self._client.pause_service.pause()
        log["consumption"] = time.time() - start_time
        self._log_list.append(log)

    async def resume(self):
        """
        Resume the simulation.

        This method sends a request to the simulator's pause service to resume the simulation.
        """
        start_time = time.time()
        log = {
            "req": "resume",
            "start_time": start_time,
            "consumption": 0
        }
        await self._client.pause_service.resume()
        log["consumption"] = time.time() - start_time
        self._log_list.append(log)

    async def get_simulator_day(self) -> int:
        """
        Get the current day of the simulation.

        - **Returns**:
            - `int`: The day number since the start of the simulation.
        """
        start_time = time.time()
        log = {
            "req": "get_simulator_day",
            "start_time": start_time,
            "consumption": 0
        }
        now = await self._client.clock_service.Now({})
        now = cast(dict[str, int], now)
        day = now["day"]
        log["consumption"] = time.time() - start_time
        self._log_list.append(log)
        return day

    async def get_simulator_second_from_start_of_day(self) -> int:
        """
        Get the number of seconds elapsed from the start of the current day in the simulation.

        - **Returns**:
            - `int`: The number of seconds from 00:00:00 of the current day.
        """
        start_time = time.time()
        log = {
            "req": "get_simulator_second_from_start_of_day",
            "start_time": start_time,
            "consumption": 0
        }
        now = await self._client.clock_service.Now({})
        now = cast(dict[str, int], now)
        log["consumption"] = time.time() - start_time
        self._log_list.append(log)
        return now["t"] % 86400

    async def get_person(self, person_id: int) -> dict:
        """
        Retrieve information about a specific person by ID.

        - **Args**:
            - `person_id` (`int`): The ID of the person to retrieve information for.

        - **Returns**:
            - `Dict`: Information about the specified person.
        """
        start_time = time.time()
        log = {
            "req": "get_person",
            "start_time": start_time,
            "consumption": 0
        }
        person = await self._client.person_service.GetPerson(
            req={"person_id": person_id}
        )  # type:ignore
        log["consumption"] = time.time() - start_time
        self._log_list.append(log)
        return person

    async def add_person(self, person: Any) -> dict:
        """
        Add a new person to the simulation.

        - **Args**:
            - `person` (`Any`): The person object to add. If it's an instance of `person_pb2.Person`,
              it will be wrapped in an `AddPersonRequest`. Otherwise, `person` is expected to already be a valid request object.

        - **Returns**:
            - `Dict`: Response from adding the person.
        """
        start_time = time.time()
        log = {
            "req": "add_person",
            "start_time": start_time,
            "consumption": 0
        }
        if isinstance(person, person_pb2.Person):
            req = person_service.AddPersonRequest(person=person)
        else:
            req = person
        person_id = await self._client.person_service.AddPerson(req)  # type:ignore
        log["consumption"] = time.time() - start_time
        self._log_list.append(log)
        return person_id

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

        - **Args**:
            - `person_id` (`int`): The ID of the person whose schedule is being set.
            - `target_positions` (`Union[List[Union[int, Tuple[int, int]]], Union[int, Tuple[int, int]]]`):
              A list of AOI or POI IDs or tuples of (AOI ID, POI ID) that the person will visit.
            - `departure_times` (`Optional[List[float]]`): Departure times for each trip in the schedule.
              If not provided, current time will be used for all trips.
            - `modes` (`Optional[List[TripMode]]`): Travel modes for each trip.
              Defaults to `TRIP_MODE_DRIVE_ONLY` if not specified.
        """
        start_time = time.time()
        log = {
            "req": "set_aoi_schedules",
            "start_time": start_time,
            "consumption": 0
        }
        cur_time = float(await self.get_time())
        if not isinstance(target_positions, list):
            target_positions = [target_positions]
        if departure_times is None:
            departure_times = [cur_time for _ in range(len(target_positions))]
        else:
            for _ in range(len(target_positions) - len(departure_times)):
                departure_times.append(cur_time)
        if modes is None:
            modes = [
                TripMode.TRIP_MODE_DRIVE_ONLY for _ in range(len(target_positions))
            ]
        else:
            for _ in range(len(target_positions) - len(modes)):
                modes.append(TripMode.TRIP_MODE_DRIVE_ONLY)
        _schedules = []
        for target_pos, _time, _mode in zip(target_positions, departure_times, modes):
            if isinstance(target_pos, int):
                if target_pos >= POI_START_ID:
                    poi_id = target_pos
                    end = {
                        "aoi_position": {
                            "aoi_id": self.poi_id_2_aoi_id[poi_id],
                            "poi_id": poi_id,
                        }
                    }
                else:
                    aoi_id = target_pos
                    end = {
                        "aoi_position": {
                            "aoi_id": aoi_id,
                        }
                    }
            else:
                aoi_id, poi_id = target_pos
                end = {"aoi_position": {"aoi_id": aoi_id, "poi_id": poi_id}}
                # activity = ""
            trips = [
                {
                    "mode": _mode,
                    "end": end,
                    "departure_time": _time,
                },
            ]
            _schedules.append(
                {"trips": trips, "loop_count": 1, "departure_time": _time}
            )
        req = {"person_id": person_id, "schedules": _schedules}
        await self._client.person_service.SetSchedule(req)
        log["consumption"] = time.time() - start_time
        self._log_list.append(log)

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

        - **Args**:
            - `person_id` (`int`): The ID of the person whose position is being reset.
            - `aoi_id` (`Optional[int]`): The ID of the Area of Interest (AOI) where the person should be placed.
            - `poi_id` (`Optional[int]`): The ID of the Point of Interest (POI) within the AOI.
            - `lane_id` (`Optional[int]`): The ID of the lane on which the person should be placed.
            - `s` (`Optional[float]`): The longitudinal position along the lane.
        """
        start_time = time.time()
        log = {
            "req": "reset_person_position",
            "start_time": start_time,
            "consumption": 0
        }
        reset_position = {}
        if aoi_id is not None:
            reset_position["aoi_position"] = {"aoi_id": aoi_id}
            if poi_id is not None:
                reset_position["aoi_position"]["poi_id"] = poi_id
            logger.debug(
                f"Setting person {person_id} pos to AoiPosition {reset_position}"
            )
            await self._client.person_service.ResetPersonPosition(
                {"person_id": person_id, "position": reset_position}
            )
        elif lane_id is not None:
            reset_position["lane_position"] = {
                "lane_id": lane_id,
                "s": 0.0,
            }
            if s is not None:
                reset_position["lane_position"]["s"] = s
            logger.debug(
                f"Setting person {person_id} pos to LanePosition {reset_position}"
            )
            await self._client.person_service.ResetPersonPosition(
                {"person_id": person_id, "position": reset_position}
            )
        else:
            logger.debug(
                f"Neither aoi or lane pos provided for person {person_id} position reset!!"
            )
        log["consumption"] = time.time() - start_time
        self._log_list.append(log)

    def get_around_poi(
        self,
        center: Union[tuple[float, float], Point],
        radius: float,
        poi_type: Union[str, list[str]],
    ) -> list[dict]:
        """
        Get Points of Interest (POIs) around a central point based on type.

        - **Args**:
            - `center` (`Union[Tuple[float, float], Point]`): The central point as a tuple or Point object.
            - `radius` (`float`): The search radius in meters.
            - `poi_type` (`Union[str, List[str]]`): The category or categories of POIs to filter by.

        - **Returns**:
            - `List[Dict]`: A list of dictionaries containing information about the POIs found.
        """
        start_time = time.time()
        log = {
            "req": "get_around_poi",
            "start_time": start_time,
            "consumption": 0
        }
        if isinstance(poi_type, str):
            poi_type = [poi_type]
        transformed_poi_type: list[str] = []
        for t in poi_type:
            if t not in self.poi_cate:
                transformed_poi_type.append(t)
            else:
                transformed_poi_type += self.poi_cate[t]
        poi_type_set = set(transformed_poi_type)
        # 获取半径内的poi
        _pois: list[dict] = self.map.query_pois(  # type:ignore
            center=center,
            radius=radius,
            return_distance=False,
        )
        # 过滤掉不满足类别前缀的poi
        pois = []
        for poi in _pois:
            catg = poi["category"]
            if catg.split("|")[-1] not in poi_type_set:
                continue
            pois.append(poi)
        log["consumption"] = time.time() - start_time
        self._log_list.append(log)
        return pois