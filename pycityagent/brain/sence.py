from typing import Optional, Union
from datetime import datetime
import math
import copy
from pycitysim.apphub import UserMessage, AgentMessage
from citystreetview import (
    BaiduStreetView,
    GoogleStreetView,
    Equirectangular,
    wgs842bd09mc,
)
from .brainfc import BrainFunction
from .static import POI_TYPE_DICT, LEVEL_ONE_PRE

def point_on_line_given_distance(start_node, end_node, distance):
    """
    Given two points (start_point and end_point) defining a line, and a distance s to travel along the line,
    return the coordinates of the point reached after traveling s units along the line, starting from start_point.

    Args:
        start_point (tuple): Tuple of (x, y) representing the starting point on the line.
        end_point (tuple): Tuple of (x, y) representing the ending point on the line.
        distance (float): Distance to travel along the line, starting from start_point.

    Returns:
        tuple: Tuple of (x, y) representing the new point reached after traveling s units along the line.
    """

    x1, y1 = start_node['x'], start_node['y']
    x2, y2 = end_node['x'], end_node['y']

    # Calculate the slope m and the y-intercept b of the line
    if x1 == x2:
        # Vertical line, distance is only along the y-axis
        return (x1, y1 + distance if distance >= 0 else y1 - abs(distance))
    else:
        m = (y2 - y1) / (x2 - x1)
        b = y1 - m * x1

        # Calculate the direction vector (dx, dy) along the line
        dx = (x2 - x1) / math.sqrt((x2 - x1)**2 + (y2 - y1)**2)
        dy = (y2 - y1) / math.sqrt((x2 - x1)**2 + (y2 - y1)**2)

        # Scale the direction vector by the given distance
        scaled_dx = dx * distance
        scaled_dy = dy * distance

        # Calculate the new point's coordinates
        x = x1 + scaled_dx
        y = y1 + scaled_dy

        return [x, y]

def get_xy_in_lane(nodes, distance, direction:str='front'):
    temp_sum = 0
    remain_s = 0
    if direction == 'front':
        # 顺道路方向前进
        if distance == 0:
            return [nodes[0]['x'], nodes[0]['y']]
        key_index = 0
        for i in range(1, len(nodes)):
            x1, y1 = nodes[i-1]['x'], nodes[i-1]['y']
            x2, y2 = nodes[i]['x'], nodes[i]['y']
            temp_sum += math.sqrt((x2 - x1)**2 + (y2-y1)**2)
            if temp_sum > distance:
                remain_s = distance - (temp_sum - math.sqrt((x2 - x1)**2 + (y2-y1)**2))
                break;
            key_index += 1
        if remain_s < 0.5:
            return [nodes[-1]['x'], nodes[-1]['y']]
        longlat = point_on_line_given_distance(nodes[key_index], nodes[key_index+1], remain_s)
        return longlat
    else:
        # 逆道路方向前进
        key_index = len(nodes)
        for i in range(len(nodes)-1, 0, -1):
            x1, y1 = nodes[i]['x'], nodes[i]['y']
            x2, y2 = nodes[i-1]['x'], nodes[i-1]['y']
            temp_sum += math.sqrt((x2 - x1)**2 + (y2-y1)**2)
            if temp_sum > distance:
                remain_s = distance - (temp_sum - math.sqrt((x2 - x1)**2 + (y2-y1)**2))
                break;
            key_index -= 1
        if remain_s < 0.5:
            return [nodes[0]['x'], nodes[0]['y']]
        longlat = point_on_line_given_distance(nodes[key_index], nodes[key_index-1], remain_s)
        return longlat

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
        
        self._engine = None
        self._baiduAK = None
        self._googleProxy = None
        self._sence_radius = sence_raduis
        """
        感知半径
        The sence raduis: meter
        """

        self._sence_contents = None
        """
        感知内容 如果为None, 则感知所有数据类型
        Sence content
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

        self._lane_type_mapping = {1: 'driving', 2: 'walking'}

    def set_sence(self, content: list):
        """
        感知配置接口

        Args:
        - config: 配置选项——包含需要感知的内容
        """
        self._sence_contents = content

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
    
    async def Sence(self):
        """
        感知功能主体
        Main function of sence

        Returns:
        - (dict): the sence content in dict format
            - time (int): current time in second (from 00:00:00)
            - pois (list[tuple]): sorted with distance
                - information of the poi
                - distance(m)
                - walking time (s)
                - walking route (list)
                - driving time (s)
                - driving route (list)
            - poi_time_walk (list[tuple]): sorted with walking time
            - poi_time_drive (list[tuple]): sorted with driving time
            - positions (list[position]): reachable positions
            - lanes
            - lane_ids
            - persons
            - streetview
            - user_messages
            - social_messages
        """
        # * time
        if self._sence_contents == None or 'time' in self._sence_contents:
            self.sence_buffer['time'] = self._agent._simulator.time

        # * pois
        if self._sence_contents == None or 'poi' in self._sence_contents:
            self.sence_buffer['pois'] = await self.PerceivePoi()
            self.sence_buffer['poi_time_walk'] = sorted(self.sence_buffer['pois'], key=lambda x:x[2])
            self.sence_buffer['poi_time_drive'] = sorted(self.sence_buffer['pois'], key=lambda x:x[4])

        # * reachable positions
        if self._sence_contents == None or 'position' in self._sence_contents:
            self.sence_buffer['positions'] = await self.PerceiveReachablePosition()

        # * lanes
        if self._sence_contents == None or 'lane' in self._sence_contents:
            self.sence_buffer['lanes'] = self.PerceiveLane()
            lane_ids = self.PerceiveLane(only_id=True)
            self.sence_buffer['lane_ids'] = lane_ids

        # * person
        if self._sence_contents == None or 'person' in self._sence_contents:
            lane_ids = self.PerceiveLane(only_id=True)
            self.sence_buffer['persons'] = []
            for lane_id in lane_ids:
                self.sence_buffer['persons'] += await self.PerceivePersonInLanes([lane_id])
            if 'aoi_position' in self._agent.motion['position'].keys():
                # 说明agent在aoi中
                persons_aoi = await self.PerceiveAoi(only_person=True)
                self.sence_buffer['persons'] += persons_aoi

        # * streetview
        if self._sence_contents == None or 'streetview' in self._sence_contents:
            if self.enable_streeview:
                self.sence_buffer['streetview'] = self.PerceiveStreetView()
            else:
                self.sence_buffer['streetview'] = None

        # * user message
        if self._sence_contents == None or 'user_message' in self._sence_contents:
            if self._agent.Hub != None:
                self.sence_buffer['user_messages'] = self.PerceiveUserMessage()
            else:
                self.sence_buffer['user_messages'] = []

        # * agent message
        if self._sence_contents == None or 'agent_message' in self._sence_contents:
            self.sence_buffer['social_messages'] = await self.PerceiveMessageFromPerson()

        # * 插件感知
        if len(self.plugs) > 0:
            for plug in self.plugs:
                out_key = plug.out
                out = plug.user_func(self.sence_buffer)
                self.plug_buffer[out_key] = out

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

    async def PerceiveReachablePosition(self, radius:int=None) -> Optional[list[dict]]:
        '''
        可达位置感知
        Reachable Position Perceive

        Args:
        - radius (int): 感知半径; Perceive radius

        Returns:
        - List[dict]: 可达位置列表
            - lane_id (int)
            - s (float)
            - longlat (Tuple[float, float]): [longitude, latitude]
            - type (str): 'driving' / 'walking' / 'unspecified'
        '''
        radius_ = self._sence_radius
        if radius != None:
            radius_ = radius
        positions = []
        if 'aoi_position' in self._agent.motion['position'].keys():
            # agent in aoi
            positions = []
            aoi_id = self._agent.motion['position']['aoi_position']['aoi_id']
            aoi = copy.deepcopy(self._agent._simulator.map.get_aoi(aoi_id))
            driving_positions = aoi['driving_positions']
            driving_gates = aoi['driving_gates']
            walking_positions = aoi['walking_positions']
            walking_gates = aoi['walking_gates']
            for i in range(len(driving_positions)):
                longlat = self._agent._simulator.map.xy2lnglat(x=driving_gates[i]['x'], y=driving_gates[i]['y'])
                positions.append({
                    'lane_id': driving_positions[i]['lane_id'], 
                    's': driving_positions[i]['s'],
                    'longlat': longlat,
                    'type': 'driving'
                })
            for i in range(len(walking_positions)):
                longlat = self._agent._simulator.map.xy2lnglat(x=walking_gates[i]['x'], y=walking_gates[i]['y'])
                positions.append({
                    'lane_id': walking_positions[i]['lane_id'], 
                    's': walking_positions[i]['s'],
                    'longlat': longlat,
                    'type': 'walking'
                })
        else:
            # agent in lane
            lane_id = self._agent.motion['position']['lane_position']['lane_id']  # 所在lane_id
            lane = copy.deepcopy(self._agnet._simualtor.map.get_lane(lane_id))  # 获取lane信息
            agent_s = self._agent.motion['position']['lane_position']['s']  # 所处位置——用s距离表示
            nodes = lane['center_line']['nodes']
            if agent_s == 0:
                # 处于当前道路的首部端点位置
                # 1. 当前道路
                tmp_s = radius_
                tmp_s = tmp_s if tmp_s <= lane['length'] else lane['length']
                x, y = get_xy_in_lane(nodes, tmp_s)
                longlat = self._agent._simulator.map.xy2lnglat(x=x, y=y)
                type = copy.deepcopy(self._lane_type_mapping.get(lane['type'], 'unspecified'))
                positions += [{'lane_id': lane_id, 's': tmp_s, 'longlat': longlat, 'type': type}]

                # 2. 前驱道路
                pre_lanes = lane['predecessors']
                for pre_lane in pre_lanes:
                    pre_lane_id = pre_lane['id']
                    pre_lane_ = copy.deepcopy(self._agent._simulator.map.get_lane(pre_lane_id))
                    pre_lane_nodes = pre_lane_['center_line']['nodes']
                    tmp_s = pre_lane_['length'] - radius_
                    tmp_s = tmp_s if tmp_s >= 0 else 0
                    x, y = get_xy_in_lane(pre_lane_nodes, tmp_s, 'back')
                    longlat = self._agent._simulator.map.xy2lnglat(x=x, y=y)
                    type = self._lane_type_mapping.get(pre_lane_['type'], 'unspecified')
                    positions += [{'lane_id': pre_lane_id, 's': tmp_s, 'longlat': longlat, 'type': type}]
            elif agent_s == lane['length']:
                # 处于当前道路的尾部端点位置
                # 1. 当前道路
                tmp_s = agent_s - radius_
                tmp_s = tmp_s if tmp_s >= 0 else 0
                x, y = get_xy_in_lane(nodes, tmp_s, 'back')
                longlat = self._agent._simulator.map.xy2loglat(x=x, y=y)
                type = self._lane_type_mapping.get(lane['type'], 'unspecified')
                positions += [{'lane_id': lane_id, 's': tmp_s, 'longlat': longlat, 'type': type}]

                # 2. 后继道路
                suc_lanes = lane['successors']
                for suc_lane in suc_lanes:
                    suc_lane_id = suc_lane['id']
                    suc_lane_ = copy.deepcopy(self._agent._simulator.map.get_lane(suc_lane_id))
                    suc_lane_nodes = suc_lane_['center_line']['nodes']
                    tmp_s = radius_
                    tmp_s = tmp_s if tmp_s <= suc_lane_['length'] else suc_lane_['length']
                    x, y = get_xy_in_lane(suc_lane_nodes, tmp_s)
                    longlat = self._agent._simulator.map.xy2loglat(x=x, y=y)
                    type = self._lane_type_mapping.get(lane['type'], 'unspecified')
                    positions += [{'lane_id': suc_lane_id, 's': tmp_s, 'longlat': longlat, 'type': type}]
            else:
                # 非端点位置
                neg_s = agent_s - radius_
                neg_s = neg_s if neg_s >= 0 else 0
                x, y = get_xy_in_lane(nodes, neg_s, 'back')
                longlat = self._agent._simulator.map.xy2loglat(x=x, y=y)
                type = self._lane_type_mapping.get(lane['type'], 'unspecified')
                positions += [{'lans_id': lane_id, 's': neg_s, 'longlat': longlat, 'type': type}]

                pos_s = agent_s + radius_
                pos_s = pos_s if pos_s <= lane['length'] else lane['length']
                x, y = get_xy_in_lane(nodes, pos_s)
                longlat = self._agent._simulator.map.xy2loglat(x=x, y=y)
                type = self._lane_type_mapping.get(lane['type'], 'unspecified')
                positions += [{'lans_id': lane_id, 's': neg_s, 'longlat': longlat, 'type': type}]
        return positions

    async def PerceivePoi(self, radius:int=None, category:str=None):
        """
        POI感知
        Sence POI

        Args:
        - radius: 感知范围, 默认使用统一感知半径. Sence raduis, default use basic radius
        - category: 6位数字类型编码, 如果为None则获取所有类型POI. 6-digit coding which represents the poi type, if None, then sence all type of poi

        Returns:
        - List[Tuple[Any, float]]: poi列表, 每个元素为:
            - poi
            - 距离: 单位m 
            - 步行前往需要的时间: 单位s, -1表示不可达或无需进入城市道路(处于同一aoi)
            - 步行路线
            - 驾车前往需要的时间: 单位s, -1表示驾车不可达或无需进入城市道路(处于同一aoi)
            - 行车路线
        """
        radius_ = self._sence_radius
        if radius != None:
            radius_ = radius
        if category != None:
            category_prefix = category
            resp = copy.deepcopy(self._agent._simulator.map.query_pois(
                center=(self._agent.motion['position']['xy_position']['x'], self._agent.motion['position']['xy_position']['y']),
                radius=radius_,
                category_prefix=category_prefix
            ))
        else:
            resp = []
            for category_prefix in LEVEL_ONE_PRE:
                resp += copy.deepcopy(self._agent._simulator.map.query_pois(
                    center=(self._agent.motion['position']['xy_position']['x'], self._agent.motion['position']['xy_position']['y']),
                    radius=radius_,
                    category_prefix=category_prefix
                ))

        # 从六位代码转变为具体类型
        results = []
        start_position = {}
        if 'aoi_position' in self._agent.motion['position']:
            start_position = {'aoi_position': {'aoi_id': self._agent.motion['position']['aoi_position']['aoi_id']}}
        else:
            start_position = {'lane_position': {'lane_id': self._agent.motion['position']['lane_position']['lane_id'], 's': self._agent.motion['position']['lane_position']['s']}}
        for poi in resp:
            cate_str = poi[0]['category']
            poi[0]['category'] = POI_TYPE_DICT[cate_str]
            info = poi[0]
            distance = poi[1]
            # walking
            rout_walking_res = await self._agent._simulator.routing.GetRoute(
                {
                    'type': 2,
                    'start': start_position,
                    'end': {'aoi_position': {'aoi_id': info['aoi_id']}},
                }
            )
            if len(rout_walking_res['journeys']) <= 0:
                walking_time = -1
                walking_route = []
            else:
                walking_time = rout_walking_res['journeys'][0]['walking']['eta']
                walking_route = rout_walking_res['journeys'][0]['walking']['route']

            # driving
            rout_driving_res = await self._agent._simulator.routing.GetRoute(
                {
                    'type': 1,
                    'start': start_position,
                    'end': {'aoi_position': {'aoi_id': info['aoi_id']}},
                }
            )
            if len(rout_driving_res['journeys']) <= 0:
                driving_time = -1
                driving_route = []
            else:
                driving_time = rout_driving_res['journeys'][0]['driving']['eta']
                driving_route = rout_driving_res['journeys'][0]['driving']['road_ids']

            # append
            results.append((info, distance, walking_time, walking_route, driving_time, driving_route))
        return results

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
            resp['roadway'] = copy.deepcopy(self._agent._simulator.map.query_lane(
                xy=(self._agent.motion['position']['xy_position']['x'], self._agent.motion['position']['xy_position']['y']),
                radius=radius_,
                lane_type=1
            ))
            resp['sidewalk'] = resp = copy.deepcopy(self._agent._simulator.map.query_lane(
                xy=(self._agent.motion['position']['xy_position']['x'], self._agent.motion['position']['xy_position']['y']),
                radius=radius_,
                lane_type=2
            ))
        elif type == 2:
            resp = copy.deepcopy(self._agent._simulator.map.query_lane(
                xy=(self._agent.motion['position']['xy_position']['x'], self._agent.motion['position']['xy_position']['y']),
                radius=radius_,
                lane_type=2
            ))
        else:
            resp = copy.deepcopy(self._agent._simulator.map.query_lane(
                xy=(self._agent.motion['position']['xy_position']['x'], self._agent.motion['position']['xy_position']['y']),
                radius=radius_,
                lane_type=1
            ))
        if only_id:
            ids = []
            for ele in resp:
                ids.append(ele[0]['id'])
            return ids
        return resp
    
    # * StreetView Related
    def PerceiveStreetView(
            self, 
            # engine:str="baidumap", 
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
        - List[PIL.Image.Image] = [left, front, right, back]
        """
        if self._engine == None:
            print("Can't get streetview, please check the streetview config")
            return []
        if self._engine == 'baidumap' and self._baiduAK == None:
            print("Can't get streetview, please provide a baidumap AK")
            return []
        if self._engine == 'googlemap' and self._googleProxy == None:
            print("Can't get streetview, please provide a googlemap proxy")
            return []

        coords = [(self._agent.motion['position']['longlat_position']['longitude'], self._agent.motion['position']['longlat_position']['latitude'])]

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
        persp = []
        if self._engine == "baidumap":
            points = wgs842bd09mc(coords, self._baiduAK)
            sv = BaiduStreetView.search(points[0][0], points[0][1])
            eq = Equirectangular(sv)
            persp.append(eq.get_perspective(120, heading_direction-90, 20, 256, 512))
            persp.append(eq.get_perspective(120, heading_direction, 20, 256, 512))
            persp.append(eq.get_perspective(120, heading_direction+90, 20, 256, 512))
            persp.append(eq.get_perspective(120, heading_direction+180, 20, 256, 512))
            if save:
                date_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                sv.panorama.save("{}/{}_{}_panorama_{}.jpg".format(save_dir, self._agent.name, date_time))
                for i in range(len(persp)):
                    persp[i].save("{}/{}_{}_persp_{}.jpg".format(save_dir, self._agent.name, date_time, i))
            return persp
        elif self._engine == "googlemap":
            sv = GoogleStreetView.search(
                    points[0][0],
                    points[0][1],
                    proxies=self._googleProxy,
                    cache_dir=save_dir
                )
            eq = Equirectangular(sv)
            persp = eq.get_perspective(120, heading_direction, 20, 256, 512)
            if save:
                date_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                sv.panorama.save("{}/{}_{}_panorama_{}.jpg".format(save_dir, self._agent.name, date_time))
                for i in range(len(persp)):
                    persp[i].save("{}/{}_{}_persp_{}.jpg".format(save_dir, self._agent.name, date_time, i))
            return persp
    
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