from typing import Optional, Union
from datetime import datetime
from pycitysim.apphub import UserMessage, AgentMessage
from citystreetview import (
    BaiduStreetView,
    GoogleStreetView,
    Equirectangular,
    wgs842bd09mc,
)
from .brainfc import BrainFunction
from .static import POI_TYPE_DICT, LEVEL_ONE_PRE

class SencePlug:
    """
    感知模块插件
    Plugin of Sence Module

    Args:
    - user_func (function): user defined function
    - out (str): the output target in sence, the sence result will be insert to Sence.plug_buffer[out]
    """
    def __init__(self, user_func, out:str) -> None:
        # TODO: 添加合法性检查
        self.user_func = user_func
        self.out = out

class Sence(BrainFunction):
    """
    Agent感知模块
    Agent Sence module
    """
    def __init__(self, agent, sence_raduis:int=10) -> None:
        super().__init__(agent)
        self._streetview_engine = ""
        self._streetviewAK = ""
        self._streetviewProxy = None
        self._sence_radius = sence_raduis
        """
        感知半径
        The sence raduis: meter
        """
        self.sence_buffer = {}
        """
        感知Buffer: 用于存储感知到的内容
        Sence Buffer: used to stroe those senced content
        """
        self.plugs = []
        """
        感知插件集合
        Collection of SencePlugs
        """
        self.plug_buffer = {}
        """
        感知插件结果Buffer: 用于存储感知插件的输出结果
        SencePlug Buffer: used to store those sence plug content
        """
        self.enable_streeview = False
        """
        街景感知功能接口, 默认为False
        Interface of streetview function, defualt: False
        """

    def add_plugs(self, plugs:list[SencePlug]):
        """
        添加感知插件
        Add SencePlug

        Args:
        - plugs (list[SencePlug]): the list of SencePlug
        """
        self.plugs += plugs

    def set_sence_radius(self, radius:int):
        """
        设置感知半径
        Set sence radius

        Args:
        - radius (int): meter
        """
        self._sence_radius = radius

    def state_influence(self):
        """
        状态-感知影响接口, 该函数会在感知前自动执行
        State-Sence influence interface, this function will be automatically invoked
        """
        return super().state_influence()
    
    async def Sence(self) -> dict:
        """
        感知功能主体
        Main function of sence

        Returns:
        - (dict): the sence content in dict format
            - time (int): current time in second (from 00:00:00)
            - pois ()
        """
        self.state_influence()
        # * time
        self.sence_buffer['time'] = self._agent._simulator.time

        # * pois
        self.sence_buffer['pois'] = self.PerceivePoi()

        # * lanes
        self.sence_buffer['lanes'] = self.PerceiveLane()
        lane_ids = self.PerceiveLane(only_id=True)
        self.sence_buffer['lane_ids'] = lane_ids

        # * person
        self.sence_buffer['persons'] = []
        for lane_id in lane_ids:
            self.sence_buffer['persons'] += await self.PerceivePersonInLanes([lane_id])
        if 'aoi_position' in self._agent.motion['position'].keys():
            # 说明agent在aoi中
            persons_aoi = await self.PerceiveAoi(only_person=True)
            self.sence_buffer['persons'] += persons_aoi

        # * streetview
        if self.enable_streeview:
            self.sence_buffer['streetview'] = self.PerceiveStreetView()
        else:
            self.sence_buffer['streetview'] = None

        # * user message
        if self._agent.Hub != None:
            self.sence_buffer['user_messages'] = self.PerceiveUserMessage()
        else:
            self.sence_buffer['user_messages'] = []

        # * agent message
        self.sence_buffer['social_messages'] = await self.PerceiveMessageFromPerson()

        # * 插件感知
        if len(self.plugs) > 0:
            for plug in self.plugs:
                out_key = plug.out
                out = plug.user_func(self.sence_buffer)
                self.plug_buffer[out_key] = out

        return self.sence_buffer

    # * AOI and POI Related
    async def PerceiveAoi(self, only_person:bool=False):
        """
        感知Agent当前所在的AOI
        Sence AOI where Agent currently in

        Args:
        - only_person (bool): whether only return persons in AOI, default: False

        Returns:
        - Union[https://cityproto.sim.fiblab.net/#city.map.v2.AoiState, list[https://cityproto.sim.fiblab.net/#city.person.v1.PersonMotion]]
        """
        resp = await self._agent._simulator._client.aoi_service.GetAoi({'aoi_ids': [self._agent.motion['position']['aoi_position']['aoi_id']]})
        if only_person:
            persons = resp['states'][0]['persons']
            return persons
        return resp['states'][0]

    def PerceivePoi(self, radius:int=None, category:str=None):
        """
        POI感知
        Sence POI

        Args:
        - radius: 感知范围, 默认使用统一感知半径. Sence raduis, default use basic radius
        - category: 6位数字类型编码, 如果为None则获取所有类型POI. 6-digit coding which represents the poi type, if None, then sence all type of poi

        Returns:
        - List[Tuple[Any, float]]: poi列表, 每个元素为(poi, 距离). poi list, each element is (poi, distance).
        """
        radius_ = self._sence_radius
        if radius != None:
            radius_ = radius
        if category != None:
            category_prefix = category
            resp = self._agent._simulator.map.query_pois(
                center=(self._agent.motion['position']['xy_position']['x'], self._agent.motion['position']['xy_position']['y']),
                radius=radius_,
                category_prefix=category_prefix
            )
        else:
            resp = []
            for category_prefix in LEVEL_ONE_PRE:
                resp += self._agent._simulator.map.query_pois(
                    center=(self._agent.motion['position']['xy_position']['x'], self._agent.motion['position']['xy_position']['y']),
                    radius=radius_,
                    category_prefix=category_prefix
                )
        # * 从六位代码转变为具体类型
        for poi in resp:
            cate_str = poi[0]['category']
            poi[0]['category'] = POI_TYPE_DICT[cate_str]
        return resp

    # * Lane Related
    def PerceiveLane(self, radius:int=None, type:int=3, only_id:bool=False) -> Union[list, dict]:
        """
        Agent视角下的Lane感知
        Lane Sence

        Args:
        - radius: 感知半径, 默认使用基础半径. Sence radius, default use basic radius
        - type: 感知的道路类型. Sence type
            - 3: 车道+人行道. drive lane + sidewalk
            - 2: 人行道. sidewalk
            - 1: 车道. drive lane
        - only_with_person: 仅返回包含人的车道. only those lanes with persons/cars
        - only_id: 仅返回laneid. only lane id

        Returns:
        - Union[list, dict]
            - if only_id, return a list of lane id
            - if sence type equal 2 or 1, return a List[Tuple[Any, float, float]]: lane列表, 每个元素为(lane, s, distance)
            - if sence type equal 3, return a dict
                - 'roadway': List[Tuple[Any, float, float]]: lane列表, 每个元素为(lane, s, distance)
                - 'sidewalk': List[Tuple[Any, float, float]]: lane列表, 每个元素为(lane, s, distance)
        """
        radius_ = self._sence_radius
        if radius != None:
            radius_ = radius
        if type == 3:
            resp = {}
            resp['roadway'] = self._agent._simulator.map.query_lane(
                xy=(self._agent.motion['position']['xy_position']['x'], self._agent.motion['position']['xy_position']['y']),
                radius=radius_,
                lane_type=1
            )
            resp['sidewalk'] = resp = self._agent._simulator.map.query_lane(
                xy=(self._agent.motion['position']['xy_position']['x'], self._agent.motion['position']['xy_position']['y']),
                radius=radius_,
                lane_type=2
            )
        elif type == 2:
            resp = self._agent._simulator.map.query_lane(
                xy=(self._agent.motion['position']['xy_position']['x'], self._agent.motion['position']['xy_position']['y']),
                radius=radius_,
                lane_type=2
            )
        else:
            resp = self._agent._simulator.map.query_lane(
                xy=(self._agent.motion['position']['xy_position']['x'], self._agent.motion['position']['xy_position']['y']),
                radius=radius_,
                lane_type=1
            )
        if only_id:
            ids = []
            for ele in resp:
                ids.append(ele[0]['id'])
            return ids
        return resp
    
    # * StreetView Related
    def PerceiveStreetView(
            self, 
            heading:str="front", 
            save:bool=False, 
            save_dir:str=None
        ):
        """
        街景图像感知
        Sence streetview

        Args:
        - engine: 需要使用的街景获取引擎. streetview engine, default: 'baidumap'
        - heading (str): 朝向，默认正前方; 同时支持back, left, right. sence towards, defualt 'front', support ['front', 'back', 'left', 'right']
        - save (bool): 是否存储. save or not
        - save_dir (str): 存储文件夹. save directory

        Returns:
        - PIL.Image.Image
        """
        coords = [(self._agent.motion['position']['longlat_position']['longitude'], self._agent.motion['position']['longlat_position']['latitude'])]
        """
        模拟人眼视角
        水平FOV: 160
        垂直角暂时不支持
        """
        if heading == "front":
            heading_direction = self._agent.motion['direction']
        elif heading == "back":
            heading_direction += 180
        elif heading == "left":
            heading_direction += -90
        elif heading == "right":
            heading_direction += 90
        else:
            print("Wrong HEADING, Use FRONT")
        if self._streetview_engine == "baidumap":
            points = wgs842bd09mc(coords, self._streetviewAK)
            sv = BaiduStreetView.search(points[0][0], points[0][1])
            eq = Equirectangular(sv)
            persp = eq.get_perspective(120, heading_direction, 20, 256, 512)
            if save:
                date_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                sv.panorama.save("{}/{}_{}_panorama.jpg".format(save_dir, self._agent.name, date_time))
                persp.save("{}/{}_{}_persp.jpg".format(save_dir, self._agent.name, date_time))
            return persp
        elif self._streetview_engine == "googlemap":
            sv = GoogleStreetView.search(
                    points[0][0],
                    points[0][1],
                    proxies=self._streetviewProxy,
                    cache_dir=save_dir
                )
            eq = Equirectangular(sv)
            persp = eq.get_perspective(120, heading_direction, 20, 256, 512)
            if save:
                sv.panorama.save("{}/{}_{}_panorama.jpg".format(save_dir, self._agent.name, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
                persp.save("{}/{}_{}_persp.jpg".format(save_dir, self._agent.name, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
            return persp
        else:
            print("Error StreetView Engine")
            return None
    
    # * Person Related
    def PerceivePersonCircule(self, raduis=30):
        """Person环形感知"""
        print("Not Implemented")
        pass

    async def PerceivePersonInLanes(self, lane_ids:list[int], only_id:bool=False):
        """
        感知指定lane集合上的person
        Sence persons in target lane collection

        Args:
        - lane_ids: 指定的lane id列表. list of lane id
        - only_id: 仅需要对应person id即可 - 否则返回person motion. whether only need person_id, default: False

        Returns:
        - Union[list[int], list[https://cityproto.sim.fiblab.net/#city.person.v1.PersonMotion]]
            - if only_id, return a list of person id
            - if not only_id, return a list of PersonMotion
        """
        req = {'lane_ids': lane_ids, 'exclude_person': False}
        resp = await self._agent._client.lane_service.GetLane(req)
        persons = []
        for lane in resp['states']:
            if only_id:
                if len(lane['persons']) > 0:
                    for pson in lane['persons']:
                        persons.append(pson['id'])
            else:
                if len(lane['persons']) > 0:
                    persons += lane['persons']
        return persons
    
    async def PerceiveMessageFromPerson(self):
        """
        接受对话消息
        Receive Conve Message

        Returns:
        - list[Message https://cityproto.sim.fiblab.net/#city.social.v1.Message]
        """
        messages = await self._agent._client.social_service.Receive({'id': self._agent._id})
        return messages['messages']
    
    def PerceiveUserMessage(self) -> list[UserMessage]:
        """
        从AppHub获取消息
        Get user messages from AppHub

        Returns:
        - list[UserMessage]
        """
        return self._agent._hub_connector.GetMessageFromHub()
    
    @property
    def Buffer(self):
        return self.sence_buffer