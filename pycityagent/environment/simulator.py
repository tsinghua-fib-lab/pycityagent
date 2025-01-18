"""Simulator: 城市模拟器类及其定义"""

import asyncio
import logging
import os
from datetime import datetime, timedelta
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


class Simulator:
    """
    - 模拟器主类
    - Simulator Class
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

    @property
    def environment(self):
        return self._environment_prompt
    
    def set_environment(self, environment: dict[str, str]):
        self._environment_prompt = environment

    def sence(self, key: str):
        return self._environment_prompt.get(key, "")
    
    def update_environment(self, key: str, value: str):
        self._environment_prompt[key] = value

    # * Agent相关
    def find_agents_by_area(self, req: dict, status=None):
        """
        通过区域范围查找agent/person
        Get agents/persons in the provided area

        Args:
        - req (dict): 用于描述区域的请求 https://cityproto.sim.fiblab.net/#city.person.1.GetPersonByLongLatBBoxRequest
        - status (int): 用于限制agent/person状态 if 'status' is not None, then you get those persons in 'status' https://cityproto.sim.fiblab.net/#city.agent.v2.Status

        Returns:
        - https://cityproto.sim.fiblab.net/#city.person.1.GetPersonByLongLatBBoxResponse
        """
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
            return resp

    def get_poi_categories(
        self,
        center: Optional[Union[tuple[float, float], Point]] = None,
        radius: Optional[float] = None,
    ) -> list[str]:
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
        return list(set(categories))

    async def get_time(
        self, format_time: bool = False, format: str = "%H:%M:%S"
    ) -> Union[int, str]:
        """
        获取模拟器当前时间 Get current time of simulator
        默认返回以00:00:00为始的, 以s为单位的时间(int)
        支持格式化时间

        Args:
        - format_time (bool): 是否格式化 format or not
        - format (str): 格式化模板，默认为"Hour:Minute:Second" the formation

        Returns:
        - time Union[int, str]: 时间 time in second(int) or formatted time(str)
        """
        now = await self._client.clock_service.Now({})
        now = cast(dict[str, int], now)
        self.time = now["t"]
        if format_time:
            current_date = datetime.now().date()
            start_of_day = datetime.combine(current_date, datetime.min.time())
            current_time = start_of_day + timedelta(seconds=now["t"])
            formatted_time = current_time.strftime(format)
            return formatted_time
        else:
            return int(now["t"])

    async def pause(self):
        await self._client.pause_service.pause()

    async def resume(self):
        await self._client.pause_service.resume()

    async def get_simulator_day(self) -> int:
        """
        获取模拟器到第几日
        """
        now = await self._client.clock_service.Now({})
        now = cast(dict[str, int], now)
        day = now["day"]
        return day

    async def get_simulator_second_from_start_of_day(self) -> int:
        """
        获取模拟器从00:00:00到当前的秒数
        """
        now = await self._client.clock_service.Now({})
        now = cast(dict[str, int], now)
        return now["t"] % 86400

    async def get_person(self, person_id: int) -> dict:
        return await self._client.person_service.GetPerson(
            req={"person_id": person_id}
        )  # type:ignore

    async def add_person(self, person: Any) -> dict:
        if isinstance(person, person_pb2.Person):
            req = person_service.AddPersonRequest(person=person)
        else:
            req = person
        return await self._client.person_service.AddPerson(req)  # type:ignore

    async def set_aoi_schedules(
        self,
        person_id: int,
        target_positions: Union[
            list[Union[int, tuple[int, int]]], Union[int, tuple[int, int]]
        ],
        departure_times: Optional[list[float]] = None,
        modes: Optional[list[TripMode]] = None,
    ):
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

    async def reset_person_position(
        self,
        person_id: int,
        aoi_id: Optional[int] = None,
        poi_id: Optional[int] = None,
        lane_id: Optional[int] = None,
        s: Optional[float] = None,
    ):
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

    def get_around_poi(
        self,
        center: Union[tuple[float, float], Point],
        radius: float,
        poi_type: Union[str, list[str]],
    ) -> list[dict]:
        if isinstance(poi_type, str):
            poi_type = [poi_type]
        transformed_poi_type = []
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
        return pois
