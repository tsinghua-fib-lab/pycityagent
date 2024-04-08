from pycityagent.urbanllm import UrbanLLM
from .urbanllm import UrbanLLM
from .agent import Agent, AgentType
from .image.image import Image
from .ac.hub_actions import PositionUpdate

class FuncAgent(Agent):
    """
    Fuctional Agent
    功能型Agent
    """

    def __init__(
            self, 
            name:str, 
            id: int,
            server:str, 
            soul:UrbanLLM=None, 
            simulator=None, 
        ) -> None:
        super().__init__(name, server, AgentType.Func, soul, simulator)
        self._id = id
        self._image = Image(self)
        """
        Func Agent画像——支持自定义内容
        """

        self.motion = {'id': id, 'position': {}, 'direction': 0}
        """
        Func Agent状态信息——与agent的sence高度相关
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
        - direction (double): 方向角
        """

    async def init_position_aoi(self, aoi_id:int):
        """
        将agent的位置初始化到指定aoi
        根据指定aoi设置aoi_position, longlat_position以及xy_position
        """
        if aoi_id in self._simulator.map.aois:
            aoi = self._simulator.map.aois[aoi_id]
            self.motion['position']['aoi_position'] = {'aoi_id': aoi_id}
            self.motion['position']['longlat_position'] = {'longitude': aoi['shapely_lnglat'].centroid.coords[0][0], 'latitude': aoi['shapely_lnglat'].centroid.coords[0][1]}
            x, y = self._simulator.map.lnglat2xy(lng=self.motion['position']['longlat_position']['longitude'], 
                                                 lat=self.motion['position']['longlat_position']['latitude'])
            self.motion['position']['xy_position'] = {'x': x, 'y': y}
        pos = PositionUpdate(self)
        await pos.Forward(longlat=[self.motion['position']['longlat_position']['longitude'], self.motion['position']['longlat_position']['latitude']])

    def Bind(self):
        """
        将智能体绑定到AppHub
        Bind the Agent with AppHub
        """
        if self._hub_connector == None:
            print("ERROR: connect with apphub first")
        else:
            self._hub_connector.InsertFuncAgent()

    def set_image(self, image: Image):
        """
        设置image——支持自由扩展Image
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
        Log信息输出
        Pring log message
        """
        pass

    @property
    def Image(self):
        """The Agent's Image"""
        return self._image