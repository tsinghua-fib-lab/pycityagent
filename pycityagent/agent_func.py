"""FuncAgent: 功能性智能体及其定义"""

from typing import Union
from pycityagent.urbanllm import UrbanLLM
from .urbanllm import UrbanLLM
from .agent import Agent, AgentType
from .image.image import Image
from .ac.hub_actions import PositionUpdate
from .utils import *
from .hubconnector import Waypoint

class FuncAgent(Agent):
    """
    Fuctional Agent
    功能型Agent
    """

    def __init__(
            self, 
            name:str, 
            server:str, 
            soul:UrbanLLM=None, 
            simulator=None, 
        ) -> None:
        """
        初始化 Init

        Args:
        - name (str): 智能体名称; name of your agent
        - id (int): 智能体Id; id of your agent
        - server (str): 模拟器grpc服务地址; server address of simulator
        - soul (UrbanLLM): 基础模型模块; base model
        - simulator (Simulator): 模拟器对象; simulator
        """

        super().__init__(name, server, AgentType.Func, soul, simulator)
        self._image = Image(self)
        """
        - Func Agent画像——支持自定义内容
        """

        self.motion = {'id': id, 'position': {}, 'direction': 0}
        """
        Func Agent状态信息——与agent的sence高度相关
        Keys:
        - id (int): 即agent id
        - position (https://cityproto.sim.fiblab.net/#city.geo.v2.Position): 即agent当前的位置描述信息
            - lane_position (dict): 当position中包含该key时表示agent当前位于lane上——与aoi_position不可同时存在
                - lane_id (int)
                - s (double)
            - aoi_position (dict): 当position中包含该key时表示agent当前位于aoi中——与lane_position不可同时存在
                - aoi_id (int)
                - poi_id (optional[int])
            - longlat_position (dict): WGS84经纬度坐标位置
                - longitude (double): 经度
                - latitude (double): 纬度
                - z (optional[double]): 高程信息
            - xy_position (dict): 坐标系表示的位置
                - x (double)
                - y (double)
                - z (double)
        - direction (double): 朝向-方向角
        """

        self._posUpdate = PositionUpdate(self)
        self._history_trajectory:list[Waypoint] = []

    async def set_position_aoi(self, aoi_id:int):
        """
        - 将agent的位置设定到指定aoi

        Args:
        - aoi_id (int): AOI id
        """
        if aoi_id in self._simulator.map.aois:
            if 'aoi_position' in self.motion['position'].keys() and aoi_id == self.motion['position']['aoi_position']['aoi_id']:
                return
            aoi = self._simulator.map.aois[aoi_id]
            self.motion['position'] = {}
            self.motion['position']['aoi_position'] = {'aoi_id': aoi_id}
            self.motion['position']['longlat_position'] = {'longitude': aoi['shapely_lnglat'].centroid.coords[0][0], 'latitude': aoi['shapely_lnglat'].centroid.coords[0][1]}
            # self._history_trajectory.append([self.motion['position']['longlat_position']['longitude'], self.motion['position']['longlat_position']['latitude']])
            x, y = self._simulator.map.lnglat2xy(lng=self.motion['position']['longlat_position']['longitude'], 
                                                 lat=self.motion['position']['longlat_position']['latitude'])
            self.motion['position']['xy_position'] = {'x': x, 'y': y}
            await self._posUpdate.Forward(longlat=[self.motion['position']['longlat_position']['longitude'], self.motion['position']['longlat_position']['latitude']])
        else:
            print("Error: wrong aoi id")

    async def set_position_lane(self, lane_id:int, s:float=0.0, direction:Union[float, str]='front'):
        """
        - 将agent的位置设定到指定lane
        
        Args:
        - lane_id (int): Lane id
        - s (float): distance from the start point of the lane, default None, if None, then set to the start point
        - direction (Union[float, str]): agent方向角, 默认值为'front'
            - float: 直接设置为给定方向角(atan2计算得到)
            - str: 可选项['front', 'back'], 指定agent的行走方向
                - 对于driving lane而言, 只能朝一个方向通行, 只能是'front'
                - 对于walking lane而言, 可以朝两个方向通行, 可以是'front'或'back'
        """
        if lane_id in self._simulator.map.lanes:
            if 'lane_position' in self.motion['position'].keys() and lane_id == self.motion['position']['lane_position']['lane_id']:
                return
            lane = self._simulator.map.lanes[lane_id]
            if s > lane['length']:
                print("Error: 's' too large")
            self.motion['position'] = {}
            self.motion['position']['lane_position'] = {'lane_id': lane_id, 's': s}
            nodes = lane['center_line']['nodes']
            x, y = get_xy_in_lane(nodes, s)
            longlat = self._simulator.map.xy2lnglat(x=x, y=y)
            self.motion['position']['longlat_position'] = {
                'longitude': longlat[0],
                'latitude': longlat[1]
            }
            self.motion['position']['xy_position'] = {
                'x': x,
                'y': y
            }
            if isinstance(direction, float):
                self.motion['direction'] = direction
            else:
                # 计算方向角
                direction_ = get_direction_by_s(nodes, s, direction)
                self.motion['direction'] = direction_      
            # self._history_trajectory.append([self.motion['position']['longlat_position']['longitude'], self.motion['position']['longlat_position']['latitude']])              
            await self._posUpdate.Forward(longlat=[self.motion['position']['longlat_position']['longitude'], self.motion['position']['longlat_position']['latitude']])
        else:
            print("Error: wrong lane id")

    async def set_position_poi(self, poi_id:int, hub:bool=True):
        """
        - 将agent的位置设定到指定poi

        Args:
        - poi_id (int): Poi id
        """
        if poi_id in self._simulator.map.pois:
            poi = self._simulator.map.pois[poi_id]
            aoi_id = poi['aoi_id']
            if 'aoi_position' in self.motion['position'].keys() and aoi_id == self.motion['position']['aoi_position']['aoi_id']:
                return
            x = poi['position']['x']
            y = poi['position']['y']
            longlat = self._simulator.map.xy2lnglat(x=x, y=y)
            self.motion['position'] = {}
            self.motion['position']['aoi_position'] = {'aoi_id': aoi_id}
            self.motion['position']['longlat_position'] = {
                'longitude': longlat[0],
                'latitude': longlat[1]
            }
            self.motion['position']['xy_position'] = {
                'x': x,
                'y': y
            }
            # self._history_trajectory.append([self.motion['position']['longlat_position']['longitude'], self.motion['position']['longlat_position']['latitude']])
            if hub:
                await self._posUpdate.Forward(longlat=[self.motion['position']['longlat_position']['longitude'], self.motion['position']['longlat_position']['latitude']])
        else:
            print("Error: wrong poi id")

    def Bind(self):
        """
        - 将智能体绑定到AppHub
        - Bind the Agent with AppHub
        """
        if self._hub_connector == None:
            print("ERROR: connect with apphub first")
        else:
            self._hub_connector.InsertFuncAgent()

    def set_image(self, image: Image):
        """
        - 设置image——支持自由扩展Image
        """
        self._image = image

    async def Step(self, log:bool):
        """
        单步Agent执行流
        Single step entrance
        (Not recommended, use Run() method)

        Args:
        - log (bool): 是否输出log信息. Whether console log message
        """
        # * 1. 模拟器时间更新
        await self._simulator.GetTime()
        # * 2. Brain工作流
        await self._brain.Run()
        # * 3. Commond Controller工作流
        command = await self._cc.Run()
        # * 4. State Transformer工作流
        self._st.trigger(command)
        # * 5. Action Controller工作流
        if self._step_with_action:
            await self._ac.Run()
        if log:
            print(f"---------------------- SIM TIME: {self._simulator.time} ----------------------")
            self.show_yourself()
    
    def show_yourself(self):
        """
        - Log信息输出
        - Pring log message
        """
        pass

    @property
    def Image(self):
        """
        - The Agent's Image
        """
        return self._image