"""Simulator: 城市模拟器类及其定义"""

from typing import Optional, Union, Tuple
from datetime import datetime, timedelta
import asyncio
from pycitydata import map
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

        self._client = CityClient(self.config['simulator']['server'], secure=True)
        """
        - 模拟器grpc客户端
        - grpc client of simulator
        """

        self.map = map.Map(
            mongo_uri = "mongodb://sim:FiblabSim1001@mgo.db.fiblab.tech:8635/",
            mongo_db = config['map_request']['mongo_db'],
            mongo_coll = config['map_request']['mongo_coll'],
            cache_dir = config['map_request']['cache_dir'],
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

        self.time = 0
        """
        - 模拟城市当前时间
        - The current time of simulator
        """
        self.poi_cate = {'10': 'eat', 
                         '13': 'shopping', 
                         '18': 'sports',
                         '22': 'excursion',
                         '16': 'entertainment',
                         '20': 'medical tratment',
                         '14': 'trivialities',
                         '25': 'financial',
                         '12': 'government and political services',
                         '23': 'cultural institutions',
                         '28': 'residence'}
        self.map_x_gap = None
        self.map_y_gap = None
        self.poi_matrix_centers = []

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
        resp = loop.run_until_complete(self._client.person_service.GetPersonByLongLatBBox(req=req))
        loop.close()
        if status == None:
            return resp
        else:
            motions = []
            for agent in resp.motions: # type: ignore
                if agent.status in status:
                    motions.append(agent)
            resp.motions = motions # type: ignore
            return resp

    def set_poi_matrix(self, map:Optional[dict]=None, row_number:int=12, col_number:int=10, radius:int=10000):
        """
        初始化pois_matrix

        Args:
        - map (dict): 地图参数
            east, west, north, south
        - row_number (int): 行数
        - col_number (int): 列数
        - radius (int): 搜索半径, 单位m
        """
        if map == None:
            self.matrix_map = self.map
        else:
            self.matrix_map = map
        print(f"Building Poi searching matrix, Row_number: {row_number}, Col_number: {col_number}, Radius: {radius}m")
        self.map_x_gap = (self.matrix_map.header['east'] - self.matrix_map.header['west']) / col_number # type: ignore
        self.map_y_gap = (self.matrix_map.header['north'] - self.matrix_map.header['south']) / row_number # type: ignore
        for i in range(row_number):
            self.poi_matrix_centers.append([])
            for j in range(col_number):
                center_x = self.matrix_map.header['west'] + self.map_x_gap*j + self.map_x_gap/2 # type: ignore
                center_y = self.matrix_map.header['south'] + self.map_y_gap*i + self.map_y_gap/2 # type: ignore
                self.poi_matrix_centers[i].append((center_x, center_y))
        
        for pre in self.poi_cate.keys():
            print(f"Building matrix for Poi category: {pre}")
            self.pois_matrix[pre] = []
            for row_centers in self.poi_matrix_centers:
                row_pois = []
                for center in row_centers:
                    pois = self.map.query_pois(center=center, radius=radius, category_prefix=pre)
                    row_pois.append(pois)
                self.pois_matrix[pre].append(row_pois)
        print("Finished")

    def get_pois_from_matrix(self, center:Tuple[float, float], prefix:str):
        """
        从poi搜索矩阵中快速获取poi

        Args:
        - center (Tuple[float, float]): 位置信息
        - prefix (str): 类型前缀
        """
        if self.map_x_gap == None:
            print("Set Poi Matrix first")
            return
        elif prefix not in self.poi_cate.keys():
            print(f"Wrong prefix, only {self.poi_cate.keys()} is usable")
            return
        elif center[0] > self.matrix_map.header['east'] or center[0] < self.matrix_map.header['west'] or center[1] > self.matrix_map.header['north'] or center[1] < self.matrix_map.header['south']: # type: ignore
            print("Wrong center")
            return
        
        # 矩阵匹配
        rows = int((center[1]-self.matrix_map.header['south'])/self.map_y_gap) # type: ignore
        cols = int((center[0]-self.matrix_map.header['west'])/self.map_x_gap) # type: ignore
        pois = self.pois_matrix[prefix][rows][cols]
        return pois
    
    def get_cat_from_pois(self, pois:list):
        cat_2_num = {}
        for poi in pois:
            cate = poi['category'][:2]
            if cate not in self.poi_cate.keys():
                continue
            if cate in cat_2_num.keys():
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
        
    def get_poi_matrix_in_rec(self, center:Tuple[float, float], radius:int=2500, rows:int=5, cols:int=5):
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
        x_gap = (east-west)/cols
        y_gap = (north-south)/rows
        matrix = []
        for i in range(rows):
            matrix.append([])
            for j in range(cols):
                matrix[i].append([])
        pois = []
        for poi in self.map.pois.values():
            x = poi['position']['x']
            y = poi['position']['y']
            if x > west and x < east and y > south and y < north:
                row_index = int((y-south)/x_gap)
                col_index = int((x-west)/y_gap)
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
                    if poi['category'][:2] in self.poi_cate.keys() and self.poi_cate[poi['category'][:2]] == matrix_type[i*cols+j]:
                        number += 1
                poi_type_number.append(number)
                
        return matrix, matrix_type, poi_total_number, poi_type_number
        
    async def GetTime(self, format_time:bool=False, format:Optional[str]="%H:%M:%S") -> Union[int, str]:
        """
        获取模拟器当前时间 Get current time of simulator
        默认返回以00:00:00为始的, 以s为单位的时间(int)
        支持格式化时间

        Args:
        - format_time (bool): 是否格式化 format or not
        - format (str): 格式化模板，默认为"Hour:Minute:Second" the formation

        Returns:
        - time Union[int, str]: 时间 time in second(int) or formated time(str)
        """
        t_sec = await self._client.clock_service.Now({})
        self.time = t_sec['t'] # type: ignore
        if format_time:
            current_date = datetime.now().date()
            start_of_day = datetime.combine(current_date, datetime.min.time())
            current_time = start_of_day + timedelta(seconds=t_sec['t']) # type: ignore
            formatted_time = current_time.strftime(format) # type: ignore
            return formatted_time
        else:
            return t_sec['t'] # type: ignore