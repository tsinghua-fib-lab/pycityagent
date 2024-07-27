"""AppHub关联Action定义"""

from typing import Callable, Optional, Any, Union
from geojson import Feature, FeatureCollection, Point, LineString
from shapely.geometry import mapping
from pycitysim.apphub import AgentMessage
from .action import HubAction
from PIL.Image import Image
from ..utils import *

class SendUserMessage(HubAction):
    """
    发送用户可见信息
    Send messages to user
    """
    def __init__(self, agent, source: str = None, before: Callable[[list], Any] = None) -> None:
        super().__init__(agent, source, before)

    async def Forward(self, messages: Optional[list[AgentMessage]] = None):
        if not messages == None:
            self._agent.Hub.Update(messages = messages)
        elif self._source != None:
            messages = self.get_source()
            if messages != None:
                self._agent.Hub.Update(messages = messages)
        else:
            print("Error: without input data")

class SendStreetview(HubAction):
    """
    发送街景图片至前端
    Send streetview to frontend
    """
    def __init__(self, agent, source: str = None, before: Callable[[list], Any] = None) -> None:
        super().__init__(agent, source, before)

    async def Forward(self, images: Optional[list[Image]] = None):
        if not images == None:
            self._agent.Hub.Update(streetview = images)
        elif self._source != None:
            images = self.get_source()
            if images != None:
                self._agent.Hub.Update(streetview = images)
        else:
            print("Error: without input data")

class SendPop(HubAction):
    """
    发送Pop信息 - agent头顶气泡信息
    Send pop message to frontend, pop message shows above the target agent
    """
    def __init__(self, agent, source: str = None, before: Callable[[list], Any] = None) -> None:
        super().__init__(agent, source, before)

    async def Forward(self, pop:Optional[str] = None):
        if not pop == None:
            self._agent.Hub.Update(pop = pop)
        elif self._source != None:
            pop = self.get_source()
            if pop != None:
                self._agent.Hub.Update(pop = pop)
        else:
            print("Error: without input data")

class PositionUpdate(HubAction):
    """
    同步当前agent的位置信息
    Send the position of current agent to frontend
    """
    def __init__(self, agent, source: str = None, before: Callable[[list], Any] = None) -> None:
        super().__init__(agent, source, before)

    async def Forward(self, longlat: Optional[list[float]] = None):
        if longlat != None:
            self._agent.Hub.Update(longlat = longlat)
        elif self._source != None:
            longlat = self.get_source()
            if longlat != None:
                self._agent.Hub.Update(longlat = longlat)
        else:
            print("Error: without input data")

class ShowPosition(HubAction):
    """
    在地图上展示特定地点
    Show a position in frontend map
    """
    def __init__(self, agent, source: str = None, before: Callable[[list], Any] = None) -> None:
        super().__init__(agent, source, before)

    async def Forward(self, position: Union[int, list[float]], properties: Optional[dict]=None):
        """
        Args:
        - position (Union[int, list[float]])
            - int: 表示poi id
            - list[float]: 具体的position经纬度坐标
        - properties (Optional[dict]): 支持用户添加自定义属性, 默认为None
            - 例如: {'description': "莲花超市"}
        """
        if isinstance(position, int):
            # poi
            if position in self._agent._simulator.map.pois:
                poi = self._agent._simulator.map.pois[position]
                lnglat_p = poi['shapely_lnglat']
                position_feature = Feature(geometry=lnglat_p, properties=properties)
                self._agent.Hub.ShowGeo(FeatureCollection([position_feature]))
            else:
                print("Error: wrong position (wrong poi id)")
        else:
            # longitude latitude
            position_feature = Feature(geometry=Point(position), properties=properties)
            self._agent.Hub.ShowGeo(FeatureCollection([position_feature]))

class ShowAoi(HubAction):
    """
    在地图上显示Aoi
    Show aoi in map
    """
    def __init__(self, agent, source: str = None, before: Callable[[list], Any] = None) -> None:
        super().__init__(agent, source, before)

    async def Forward(self, aoi_id:int, properties: Optional[dict]=None):
        """
        Args:
        - aoi_id (int): Aoi id
        - properties (Optional[dict]): 支持用户添加自定义属性, 默认为None
            - 例如: {'description': "我居住的小区"}
        """
        properties_default = {
            "stroke-width": 2,
            "stroke-opacity": 1,
            "fill": "#ff2600",
            "fill-opacity": 0.5
        }
        if properties != None:
            properties_default.update(properties)
        if aoi_id in self._agent._simulator.map.aois:
            aoi = self._agent._simulator.map.aois[aoi_id]
            lnglat_poly = aoi['shapely_lnglat']
            aoi_feature = Feature(geometry=lnglat_poly, properties=properties_default)
            self._agent.Hub.ShowGeo(FeatureCollection([aoi_feature]))
        else:
            print("Error: wrong aoi id")

class ShowPath(HubAction):
    """
    在地图上展示路径信息
    Show a path in frontend map
    """
    def __init__(self, agent, source: str = None, before: Callable[[list], Any] = None) -> None:
        super().__init__(agent, source, before)

    async def Forward(self, 
                      path: Optional[Union[int, list[list[float]]]]=None, 
                      start_end: Optional[Union[float, tuple[float, float]]]=None, 
                      direction: Optional[str]='front', 
                      properties: Optional[dict]=None):
        """
        Args:
        - path (Optional[Union[int, list[list[float]]]]): 如果为None, 从Reason池中基于source拿取数据
            - int: lane id
            - list[list[float]]: path node
        - start_end: (Optional[Union[float, tuple[float, float]]]): 指定显示范围, 如path是list[list[float]]形式则无效
            - float: 如果仅包含一个float, 则展示从指定位置开始到path结尾的位置
            - tuple[float, end]: 分别表示起点与终点
        - direction (str): 指定前进方向, 支持['front', 'back'], 默认为'front'
        - properties (Optional[dict]): 支持用户添加自定义属性, 默认为None
        """
        properties_default = {'stroke-width': 10, 'stroke-opacity': 0.5}
        if properties != None:
            properties_default.update(properties)
        if path != None:
            if isinstance(path, int):
                # lane id
                if path in self._agent._simulator.map.lanes:
                    lane = self._agent._simulator.map.lanes[path]
                    nodes = lane['center_line']['nodes']
                    path_ls = mapping(lane['shapely_lnglat'])
                    path_ls['coordinates'] = list(path_ls['coordinates'])
                    for i in range(len(path_ls['coordinates'])):
                        path_ls['coordinates'][i] = list(path_ls['coordinates'][i])
                    # start-end与direction处理
                    if isinstance(start_end, float):
                        # start
                        if direction == 'back':
                            key_index = get_keyindex_in_lane(nodes, start_end, 'back')
                            path_ls['coordinates'] = path_ls['coordinates'][:key_index+1]
                            path_ls['coordinates'].reverse()
                        else:
                            key_index = get_keyindex_in_lane(nodes, start_end)
                            path_ls['coordinates'] = path_ls['coordinates'][key_index:]

                        path_ls['coordinates'][0] = [
                                self._agent.motion['position']['longlat_position']['longitude'],
                                self._agent.motion['position']['longlat_position']['latitude']
                            ]
                    elif isinstance(start_end, tuple) and len(start_end) == 2:
                        # start - end
                        start = start_end[0]
                        end = start_end[1]
                        if direction == 'back':
                            keyIndex_s = get_keyindex_in_lane(nodes, start, 'back')
                            keyIndex_e = get_keyindex_in_lane(nodes, end, 'back')
                            path_ls['coordinates'] = path_ls['coordinates'][keyIndex_e:keyIndex_s+1]
                            path_ls['coordinates'].reverse()
                            xy = get_xy_in_lane(nodes, end, 'back')
                            longlat = self._agent._simulator.map.xy2lnglat(x=xy[0], y=xy[1])
                            path_ls['coordinates'].append([longlat[0], longlat[1]])
                        else:
                            keyIndex_s = get_keyindex_in_lane(nodes, start)
                            keyIndex_e = get_keyindex_in_lane(nodes, end)
                            path_ls['coordinates'] = path_ls['coordinates'][keyIndex_s:keyIndex_e+1]
                            xy = get_xy_in_lane(nodes, end)
                            longlat = self._agent._simulator.map.xy2lnglat(x=xy[0], y=xy[1])
                            path_ls['coordinates'].append([longlat[0], longlat[1]])
                        path_ls['coordinates'][0] = [
                                    self._agent.motion['position']['longlat_position']['longitude'],
                                    self._agent.motion['position']['longlat_position']['latitude']
                                ]
                    path_feature = Feature(geometry=path_ls, properties=properties_default)
                    self._agent.Hub.ShowGeo(FeatureCollection([path_feature]))
                else:
                    print("Error: wrong path (wrong lane id)")
            else:
                # list point
                path_ls = LineString(path)
                path_feature = Feature(geometry=path_ls, properties=properties_default)
                self._agent.Hub.ShowGeo(FeatureCollection([path_feature]))
        elif self._source != None:
            path_coll = self.get_source()
            if path_coll != None:
                path = path_coll['path']
                start_end = path_coll['start_end']
                direction = path_coll['direction']
                properties = path_coll['properties']
                if properties != None:
                    properties_default.update(properties)
                if isinstance(path, int):
                    # lane id
                    if path in self._agent._simulator.map.lanes:
                        lane = self._agent._simulator.map.lanes[path]
                        nodes = lane['center_line']['nodes']
                        path_ls = mapping(lane['shapely_lnglat'])
                        path_ls['coordinates'] = list(path_ls['coordinates'])
                        for i in range(len(path_ls['coordinates'])):
                            path_ls['coordinates'][i] = list(path_ls['coordinates'][i])
                        # start-end与direction处理
                        if isinstance(start_end, float):
                            # start
                            if direction == 'back':
                                key_index = get_keyindex_in_lane(nodes, start_end, 'back')
                                path_ls['coordinates'] = path_ls['coordinates'][:key_index+1]
                                path_ls['coordinates'].reverse()
                            else:
                                key_index = get_keyindex_in_lane(nodes, start_end)
                                path_ls['coordinates'] = path_ls['coordinates'][key_index:]

                            path_ls['coordinates'][0] = [
                                    self._agent.motion['position']['longlat_position']['longitude'],
                                    self._agent.motion['position']['longlat_position']['latitude']
                                ]
                        elif isinstance(start_end, tuple) and len(start_end) == 2:
                            # start - end
                            start = start_end[0]
                            end = start_end[1]
                            if direction == 'back':
                                keyIndex_s = get_keyindex_in_lane(nodes, start, 'back')
                                keyIndex_e = get_keyindex_in_lane(nodes, end, 'back')
                                path_ls['coordinates'] = path_ls['coordinates'][keyIndex_e:keyIndex_s+1]
                                path_ls['coordinates'].reverse()
                                xy = get_xy_in_lane(nodes, end, 'back')
                                longlat = self._agent._simulator.map.xy2lnglat(x=xy[0], y=xy[1])
                                path_ls['coordinates'].append([longlat[0], longlat[1]])
                            else:
                                keyIndex_s = get_keyindex_in_lane(nodes, start)
                                keyIndex_e = get_keyindex_in_lane(nodes, end)
                                path_ls['coordinates'] = path_ls['coordinates'][keyIndex_s:keyIndex_e+1]
                                xy = get_xy_in_lane(nodes, end)
                                longlat = self._agent._simulator.map.xy2lnglat(x=xy[0], y=xy[1])
                                path_ls['coordinates'].append([longlat[0], longlat[1]])
                            path_ls['coordinates'][0] = [
                                        self._agent.motion['position']['longlat_position']['longitude'],
                                        self._agent.motion['position']['longlat_position']['latitude']
                                    ]
                        path_feature = Feature(geometry=path_ls, properties=properties_default)
                        self._agent.Hub.ShowGeo(FeatureCollection([path_feature]))
                    else:
                        print("Error: wrong path (wrong lane id)")
                else:
                    # list point
                    path_ls = LineString(path)
                    path_feature = Feature(geometry=path_ls, properties=properties_default)
                    self._agent.Hub.ShowGeo(FeatureCollection([path_feature]))
        else:
            print("Error: without input")