"""Simulator: 城市模拟器类及其定义"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Any, Optional, Tuple, Union, cast

from mosstool.type import TripMode
from pycitydata.map import Map as SimMap
from pycityproto.city.person.v2 import person_pb2 as person_pb2
from pycityproto.city.person.v2 import person_service_pb2 as person_service

from .sim import CityClient


class Simulator:
    """
    - 模拟器主类
    - Simulator Class
    """

    def __init__(self, config) -> None:
        self.config = config
        """
        - 模拟器配置
        - simulator config
        """

        self._client = CityClient(self.config["simulator"]["server"], secure=True)
        """
        - 模拟器grpc客户端
        - grpc client of simulator
        """

        self.map = SimMap(
            mongo_uri=config["map_request"]["mongo_uri"],
            mongo_db=config["map_request"]["mongo_db"],
            mongo_coll=config["map_request"]["mongo_coll"],
            cache_dir=config["map_request"]["cache_dir"],
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
        self.poi_cate = {
            "10": "eat",
            "13": "shopping",
            "18": "sports",
            "22": "excursion",
            "16": "entertainment",
            "20": "medical tratment",
            "14": "trivialities",
            "25": "financial",
            "12": "government and political services",
            "23": "cultural institutions",
            "28": "residence",
        }
        self.map_x_gap = None
        self.map_y_gap = None
        self._bbox: Tuple[float, float, float, float] = (-1, -1, -1, -1)
        self.poi_matrix_centers = []
        self._lock = asyncio.Lock()

    # * Agent相关
    def FindAgentsByArea(self, req: dict, status=None):
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

    def set_poi_matrix(
        self, row_number: int = 12, col_number: int = 10, radius: int = 10000
    ):
        """
        初始化pois_matrix

        Args:
        - map (dict): 地图参数
            east, west, north, south
        - row_number (int): 行数
        - col_number (int): 列数
        - radius (int): 搜索半径, 单位m
        """
        self.matrix_map = self.map
        map_header = self.matrix_map.header
        min_x, min_y, max_x, max_y = (
            map_header[k] for k in ("west", "south", "east", "north")
        )
        self._bbox = (min_x, min_y, max_x, max_y)
        logging.info(
            f"Building Poi searching matrix, Row_number: {row_number}, Col_number: {col_number}, Radius: {radius}m"
        )
        self.map_x_gap = map_x_gap = (max_x - min_x) / col_number
        self.map_y_gap = map_y_gap = (max_y - min_y) / row_number
        self.poi_matrix_centers = poi_matrix_centers = [[] for _ in range(row_number)]
        for i, i_centers in enumerate(poi_matrix_centers):
            for j in range(col_number):
                center_x = map_header["west"] + map_x_gap * j + map_x_gap / 2
                center_y = map_header["south"] + map_y_gap * i + map_y_gap / 2
                i_centers.append((center_x, center_y))

        for pre, _ in self.poi_cate.items():
            logging.info(f"Building matrix for Poi category: {pre}")
            self.pois_matrix[pre] = []
            for row_centers in self.poi_matrix_centers:
                row_pois = []
                for center in row_centers:
                    pois = self.map.query_pois(
                        center=center, radius=radius, category_prefix=pre
                    )
                    row_pois.append(pois)
                self.pois_matrix[pre].append(row_pois)
        logging.info("Finished")

    def get_pois_from_matrix(self, center: Tuple[float, float], prefix: str):
        """
        从poi搜索矩阵中快速获取poi

        Args:
        - center (Tuple[float, float]): 位置信息
        - prefix (str): 类型前缀
        """
        (min_x, min_y, max_x, max_y) = self._bbox
        _x, _y = center
        if self.map_x_gap is None or self.map_y_gap is None:
            logging.warning("Set Poi Matrix first")
            return
        elif prefix not in self.poi_cate:
            logging.warning(f"Wrong prefix, only {self.poi_cate.keys()} is usable")
            return
        elif not (min_x < _x < max_x) or not (min_y < _y < max_y):
            logging.warning("Wrong center")
            return

        # 矩阵匹配
        rows = int((_y - min_y) / self.map_y_gap)
        cols = int((_x - min_x) / self.map_x_gap)
        pois = self.pois_matrix[prefix][rows][cols]
        return pois

    def get_cat_from_pois(self, pois: list):
        cat_2_num = {}
        for poi in pois:
            cate = poi["category"][:2]
            if cate not in self.poi_cate:
                continue
            if cate in cat_2_num:
                cat_2_num[cate] += 1
            else:
                cat_2_num[cate] = 1
        max_cat = ""
        max_num = 0
        for key in cat_2_num.keys():
            if cat_2_num[key] > max_num:
                max_num = cat_2_num[key]
                max_cat = self.poi_cate[key]
        return max_cat

    def get_poi_matrix_in_rec(
        self,
        center: Tuple[float, float],
        radius: int = 2500,
        rows: int = 5,
        cols: int = 5,
    ):
        """
        获取以center为中心的正方形区域内的poi集合

        Args:
        - center (Tuple[float, float]): 中心位置点
        - radius (int): 半径
        """
        north = center[1] + radius
        south = center[1] - radius
        west = center[0] - radius
        east = center[0] + radius
        x_gap = (east - west) / cols
        y_gap = (north - south) / rows
        matrix = []
        for i in range(rows):
            matrix.append([])
            for j in range(cols):
                matrix[i].append([])
        for poi in self.map.pois.values():
            x = poi["position"]["x"]
            y = poi["position"]["y"]
            if west < x < east and south < y < north:
                row_index = int((y - south) / x_gap)
                col_index = int((x - west) / y_gap)
                matrix[row_index][col_index].append(poi)
        matrix_type = []
        for i in range(rows):
            for j in range(cols):
                matrix_type.append(self.get_cat_from_pois(matrix[i][j]))
        poi_total_number = []
        poi_type_number = []
        for i in range(rows):
            for j in range(cols):
                poi_total_number.append(len(matrix[i][j]))
                number = 0
                for poi in matrix[i][j]:
                    if (
                        poi["category"][:2] in self.poi_cate.keys()
                        and self.poi_cate[poi["category"][:2]]
                        == matrix_type[i * cols + j]
                    ):
                        number += 1
                poi_type_number.append(number)

        return matrix, matrix_type, poi_total_number, poi_type_number

    async def GetTime(
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

    async def GetPerson(self, person_id: int) -> dict:
        return await self._client.person_service.GetPerson(
            req={"person_id": person_id}
        )  # type:ignore

    async def AddPerson(self, person: Any) -> dict:
        if isinstance(person, person_pb2.Person):
            req = person_service.AddPersonRequest(person=person)
        else:
            req = person
        return await self._client.person_service.AddPerson(req)  # type:ignore

    async def SetAoiSchedules(
        self,
        person_id: int,
        target_positions: Union[
            list[Union[int, tuple[int, int]]], Union[int, tuple[int, int]]
        ],
        departure_times: Optional[list[float]] = None,
        modes: Optional[list[TripMode]] = None,
    ):
        cur_time = float(await self.GetTime())
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

    async def ResetPersonPosition(
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
