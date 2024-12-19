"""Simulator: 城市模拟器类及其定义"""

import asyncio
import logging
import os
from collections import defaultdict
from collections.abc import Sequence
from datetime import datetime, timedelta
from typing import Any, Optional, Tuple, Union, cast

from mosstool.type import TripMode
from mosstool.util.format_converter import coll2pb
from pycitydata.map import Map as SimMap
from pycityproto.city.map.v2 import map_pb2 as map_pb2
from pycityproto.city.person.v2 import person_pb2 as person_pb2
from pycityproto.city.person.v2 import person_service_pb2 as person_service
from pymongo import MongoClient
from shapely.geometry import Point
from shapely.strtree import STRtree

from .sim import CityClient, ControlSimEnv
from .utils.const import *


class Simulator:
    """
    - 模拟器主类
    - Simulator Class
    """

    def __init__(self, config, secure: bool = False) -> None:
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
            if "server" not in config["simulator"]:
                self._sim_env = sim_env = ControlSimEnv(
                    task_name=config["simulator"].get("task", "citysim"),
                    map_file=_map_pb_path,
                    start_step=config["simulator"].get("start_step", 0),
                    total_step=2147000000,
                    log_dir=config["simulator"].get("log_dir", "./log"),
                    min_step_time=config["simulator"].get("min_step_time", 1000),
                    simuletgo_addr=config["simulator"].get("server", None),
                )

                # using local client
                self._client = CityClient(sim_env.simuletgo_addr, secure=False)
                """
                - 模拟器grpc客户端
                - grpc client of simulator
                """
            else:
                self._client = CityClient(config["simulator"]["server"], secure=False)
        else:
            logging.warning(
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

        self.pois_matrix: dict[str, list[list[list]]] = {}
        """
        pois的基于区块的划分——方便快速粗略地查询poi
        通过Simulator.set_pois_matrix()初始化
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
        self.poi_matrix_centers = []
        self._lock = asyncio.Lock()
        # poi STRtree
        self.set_poi_tree()

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

    def set_poi_tree(
        self,
    ):
        """
        初始化pois_tree
        """
        poi_geos = []
        tree_id_2_poi_and_catg: dict[int, tuple[dict, str]] = {}
        for tree_id, poi in enumerate(self.map.pois.values()):
            tree_id_2_poi_and_catg[tree_id] = (poi, poi["category"])
            poi_geos.append(Point([poi["position"][k] for k in ["x", "y"]]))
        self.tree_id_2_poi_and_catg = tree_id_2_poi_and_catg
        self.pois_tree = STRtree(poi_geos)

    def get_poi_categories(
        self,
        center: Optional[Union[tuple[float, float], Point]] = None,
        radius: Optional[float] = None,
    ) -> list[str]:
        if center is not None and radius is not None:
            if not isinstance(center, Point):
                center = Point(center)
            indices = self.pois_tree.query(center.buffer(radius))
        else:
            indices = list(self.tree_id_2_poi_and_catg.keys())
        categories = []
        for index in indices:
            _, catg = self.tree_id_2_poi_and_catg[index]
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
        t_sec = await self._client.clock_service.Now({})
        t_sec = cast(dict[str, int], t_sec)
        self.time = t_sec["t"]
        if format_time:
            current_date = datetime.now().date()
            start_of_day = datetime.combine(current_date, datetime.min.time())
            current_time = start_of_day + timedelta(seconds=t_sec["t"])
            formatted_time = current_time.strftime(format)
            return formatted_time
        else:
            return t_sec["t"]

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
            logging.debug(
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
            logging.debug(
                f"Setting person {person_id} pos to LanePosition {reset_position}"
            )
            await self._client.person_service.ResetPersonPosition(
                {"person_id": person_id, "position": reset_position}
            )
        else:
            logging.debug(
                f"Neither aoi or lane pos provided for person {person_id} position reset!!"
            )

    def get_around_poi(
        self,
        center: Union[tuple[float, float], Point],
        radius: float,
        poi_type: Union[str, list[str]],
    ):
        if not isinstance(poi_type, Sequence):
            poi_type = [poi_type]
        transformed_poi_type = []
        for t in poi_type:
            if t not in self.poi_cate:
                transformed_poi_type.append(t)
            else:
                transformed_poi_type += self.poi_cate[t]
        poi_type_set = set(transformed_poi_type)
        if not isinstance(center, Point):
            center = Point(center)
        # 获取半径内的poi
        indices = self.pois_tree.query(center.buffer(radius))
        # 过滤掉不满足类别前缀的poi
        pois = []
        for index in indices:
            poi, catg = self.tree_id_2_poi_and_catg[index]
            if catg.split("|")[-1] not in poi_type_set:
                continue
            pois.append(poi)
        return pois
