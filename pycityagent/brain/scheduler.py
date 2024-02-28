from enum import Enum
import random
import time as Time
import json
from .brainfc import BrainFunction
from pycitysim.apphub import AgentMessage

# 1: walk; 2: drive
MODE = [1, 2]

class ScheduleType(Enum):
    """
    枚举规划类型
    Enum: the schedule type
        - Trip: 出行规划. Trip Schedule
        - Shop: 购物规划. Shop Schedule
        - Other: 其他规划. Other Schedule
    """
    TRIP = 1
    SHOP = 2
    OTHER = 3

class Schedule:
    def __init__(self, type) -> None:
        '''默认初始化'''
        self.type = type

class TripSchedule(Schedule):
    """
    出行规划
    Trip Schedule
    """
    def __init__(self, target_id_aoi:int, target_id_poi:int, name:str, mode:int, time:float, description:str) -> None:
        super().__init__(ScheduleType.TRIP)
        self.target_id_aoi = target_id_aoi
        """the aoi id of destination"""
        self.target_id_poi = target_id_poi
        """the poi id of destination"""
        self.name = name
        """the name of destination"""
        self.mode = mode
        """the trip mode of destination, 1:walk, 2:drive"""
        self.time = time
        """the start time of trip"""
        self.description = description
        """the desctiption of the trip"""
        self.is_set = False
        """whether this trip has sync to AppHub/simulator"""
        self.arrived = False
        """whether has arrived"""
        self.route_chance = 10
        """the chance for route, subtract 1 each time, if reduced to 0 then route failed"""
        self.route_failed = False
        """whether route failed"""

    def __str__(self) -> str:
        text = ''''''
        text += f'[类型: {self.type}, 目的地: {self.target_id_aoi}-{self.target_id_poi}-{self.name}, 方式: {self.mode}, 时间: {self.time}, 描述: {self.description}, 是否同步至模拟器: {self.is_set}]\n'
        return text

class ShopSchedule(Schedule):
    """
    购物规划
    Shop Schedule
    """
    def __init__(self, target_id_aoi:int, target_id_poi:int, name:str, description:str) -> None:
        super().__init__(ScheduleType.SHOP)
        self.target_id_aoi = target_id_aoi
        """the aoi id of destination"""
        self.target_id_poi = target_id_poi
        """the poi id of destination"""
        self.name = name
        """the name of destination"""
        self.description = description
        """the description of this schedule"""
        self.arrived = False
        """whether arrived destination"""
        self.finished = False
        """whether finished shop"""

    def __str__(self) -> str:
        text = ''''''
        text += f'[类型: {self.type}, 目的地: {self.target_id_aoi}-{self.target_id_poi}-{self.name}, 描述: {self.description}]\n'
        return text

class OtherSchdule(Schedule):
    """
    其他规划
    Other Schedule
    """
    def __init__(self, target_id_aoi:int, target_id_poi:int, name:str, description:str, duration:int) -> None:
        super().__init__(ScheduleType.OTHER)
        self.target_id_aoi = target_id_aoi
        """the aoi id of destination"""
        self.target_id_poi = target_id_poi
        """the poi id of destination"""
        self.name = name
        """the name of destination"""
        self.description = description
        """the desctription of this schedule"""
        self.duration = duration
        """the duration of activity"""
        self.remain = duration
        """the remaining time of activity"""
        self.finished = False
        """whether finished this schedule"""

    def __str__(self) -> str:
        text = ''''''
        text += f'[类型: {self.type}, 描述: {self.description}, 持续时间: {self.duration}]\n'
        return text

class Scheduler(BrainFunction):
    """
    规划器
    Agent Scheduler
    """
    def __init__(self, agent) -> None:
        super().__init__(agent)
        self.base_schedule = []
        """the basic schedules, which sync from databse"""
        self.base_schedule_index = -1
        """the index of current base schedule"""
        self.is_controled = False
        """whether the agent in 'controled' state"""
        self.user_commond_schedule = []
        """the user commond schedules, which are generated from user commond"""
        self.commond_schedule_index = -1
        """the index of user schedules"""
        self.now = None
        """the current schedule"""
        self.history = []
        """the history schedules"""
        self.need_schedule = False
        """whether need schedule"""
        self.pre_time = None

    def clear_user_schedule(self):
        """
        清空用户规划
        Clear user commond scheudles
            - set is_controled to False
            - clear user_commond_schedule
            - set commond_schedule_index to 0
        """
        self.is_controled = False
        self.user_commond_schedule = []
        self.commond_schedule_index = 0

    def clear_base_schedule(self):
        """
        清空基础规划
        Clear base schedules
        """
        for sche in self.base_schedule:
            if sche.type.value == ScheduleType.TRIP.value:
                sche.route_change = 10
                sche.route_failed = False
                sche.is_set = False
                sche.arrived = False
            elif sche.type.value == ScheduleType.SHOP.value:
                sche.arrived = False
                sche.finished = False
            elif sche.type.value == ScheduleType.OTHER.value:
                sche.fnished = False

    def unset_schedule(self):
        """
        重设规划标志
        Unset schedule attributes
        """
        if self.now != None and self.now.type.value == ScheduleType.TRIP.value:
            self.now.is_set = False
        for sche in self.user_commond_schedule:
            if sche.type.value == ScheduleType.TRIP.value:
                sche.is_set = False

    async def schedule(self, current_target: str, commond:bool=True):        
        """
        规划
        Schedule function

        Args:
        - current_target (str): 规划目标. the schedule target
        - commond (str): 是否基于用户命令进行规划. whether based on user commond, default: True

        Returns:
        - int: return 0 if success, else failed
        """
        # * 前置配置流程
        if commond:
            self.clear_user_schedule()
        else:
            pass
        schedules = []

        # * 主行程规划流程
        dialog = [
            {'role': 'system', 'content': '你是一名行程规划大师, 行程表示一次出行，你需要基于用户提供的基本信息帮助用户完成行程规划.'},
            {'role': 'system', 'content': '用户输入信息包含四部分: [用户基本信息], [空间信息], [当前时间], [行程规划目标]'},
            {'role': 'system', 'content': '''[用户基本信息]中包含用户的个人基本信息'''},
            {'role': 'system', 'content': '''[空间信息]包含所有可选的, 可能出现在你的回答中的地点信息.
            空间信息中对每个地点的描述格式如下: 
            {"id": 地点对应的id, "name": 地点对应的名称, "category": 地点对应的类型, "aoi_id": 与地点关联的AOI id, "relation": 该地点与用户的关系}'''},
            {'role': 'system', 'content': '[当前时间]以从当前00:00:00开始到目前时间的以秒为单位的整数表达: 例如21600表示实际当前时间为6:00:00'},
            {'role': 'system', 'content': '[行程规划目标]表示用户当前最急切的行程需求, 你的回答应尽可能满足用户的行程规划目标'},
            {'role': 'system', 'content': '''你的回答应该严格按照规定格式给出, 一条行程安排的格式为(请勿包含冗余信息!):
            {"id": 目标地点的id, "aoi_id": 与目标地点关联的AOI id, "time": 开始该行程的时间, 请用与当前时间相同的格式给出(一个整数), "explaination": 安排该行程的理由(从用户的第一视角回答, 以[我]为主语)}'''},
            {'role': 'system', 'content': '''如你需要给出多条行程安排, 请以列表形式给出, 例如: [行程1, 行程2]'''}
        ]
        user_profile = self._agent.Image.get_profile()
        dialog += [{'role': 'user', 'content': f'[用户基本信息]: \n{user_profile}'}]
        user_spatial_knowledge = self._agent.Brain.Memory.Spatial.to_dialog_str()
        dialog += [{'role': 'user', 'content': f'[空间信息]: \n{user_spatial_knowledge}'}]
        current_time = self._agent._simulator.time
        dialog += [{'role': 'user', 'content': f'[当前时间]: {int(current_time)}'}]
        dialog += [{'role': 'user', 'content': f'[行程规划目标]: {current_target}'}]
        print(f'''
==============================================
{dialog}
==============================================
''')
        try:
            resp = self._agent._soul.text_request(dialog)
            print(f'规划结果: 【{resp}】')
            resp_dict = json.loads(resp)
        except:
            print("行程规划失败")
            return -1
        
        # * 进行解析
        for trip in resp_dict:
            poi_id = trip['id']
            aoi_id = trip['aoi_id']
            time = trip['time']
            description = trip['explaination']
            if poi_id in self._agent.Brain.Memory.Spatial.spatial_dict.keys():
                name = self._agent.Brain.Memory.Spatial.spatial_dict[poi_id]['name']
            else:
                name = '未知地点'
            mesg = f'''前往{name}-({aoi_id}), {description}'''
            self._agent.Hub.Update([AgentMessage(self._agent.Hub._agent_id, int(Time.time()*1000), mesg, None, None)])
            if 'aoi_position' in self._agent.motion['position'].keys():
                mode = random.choice(MODE)
            else:
                lane_id = self._agent.motion['position']['lane_position']['lane_id']
                if self._agent._simulator.map.lanes[lane_id]['type'] == 1:
                    mode = 2
                else:
                    mode = 1
            schedule = TripSchedule(aoi_id, poi_id, name, mode, time, description)
            schedules.append(schedule)
            # * 后续行程推理
            contin_dialog = [
                {'role': 'system', 'content': '''你是一名活动预测大师, 你将基于用户输入的当前行程描述, 判断用户在该行程结束后将进行何种活动, 并从用户的第一视角对该活动进行解释'''},
                {'role': 'system', 'content': '''你的输出需要严格按照以下格式给出: 
                {"type": 表示活动类型, 可选结果包括[购物, 工作, 休息, 其他](其中之一), "duration": 该项活动的持续时间(以秒为单位表示的整数), "description": 第用户视角出发的对该活动的解释}'''},
                {'role': 'system', 'content': '''例如用户输入: 我要去学校工作，你将输出: {'type': "工作", "duration": 7200, "description": "在学校工作"}'''},
                {'role': 'system', 'content': '''例如用户输入: 我要去周围购买生活用品, 你将输出: {"type": "购物", "duration": 1800, "description": "购买生活用品"}'''}
            ]
            contin_dialog += [{'role': 'user', 'content': description}]
            print(contin_dialog)
            resp_more = self._agent._soul.text_request(contin_dialog)
            print(resp_more)
            try:
                resp_more_dict = json.loads(resp_more)
                print(resp_more_dict)
                if resp_more_dict['type'] == '购物':
                    schedule = ShopSchedule(aoi_id, poi_id, name, resp_more_dict['description'])
                else:
                    schedule = OtherSchdule(aoi_id, poi_id, name, resp_more_dict['description'], resp_more_dict['duration'])
                schedules.append(schedule)
            except:
                print("后续行程推理失败")

        # * 后处理流
        if commond:
            self.user_commond_schedule = schedules
            self.is_controled = True
            self.now = None
        else:
            pass
        return 0

    async def schedule_forward(self):
        """
        基于规划集合的执行流
        The stream function based on schedule collection
        """
        now_time = self._agent._simulator.time
        # * check new day
        if self.pre_time != None and now_time < self.pre_time:
            # 新的一天重设标志
            self.clear_base_schedule()
            self.base_schedule_index = 0

        if self._agent.state == 'trip' and self.now != None:
            # * 判断是否达到目的地
            if 'aoi_position' in self._agent.motion['position'].keys() and self._agent.motion['position']['aoi_position']['aoi_id'] == self.now.target_id_aoi:
                self.now.arrived = True
            # * 判断导航请求是否失败
            if self._agent.motion['status'] == 6:
                # 重试机会
                self.now.route_chance -= 1
                if self.now.route_chance <= 0:
                    # 导航请求失败
                    self.now.route_failed = True
        elif self._agent.state == 'idle':
            # * 在idle状态下进行行程检查与调整
            # * new day
            if self.now == None:
                # * 当前无行程
                if self.is_controled:
                    # * 用户行程注册
                    if self.user_commond_schedule[self.commond_schedule_index].type.value == ScheduleType.TRIP.value:
                        # * 对于trip类型的schedule
                        if self.user_commond_schedule[self.commond_schedule_index].time <= self._agent._simulator.time:
                            self.now = self.user_commond_schedule[self.commond_schedule_index]
                            if 'aoi_position' in self._agent.motion['position'].keys() and self._agent.motion['position']['aoi_position']['aoi_id'] == self.now.target_id_aoi:
                                # 如果当前已经在目的地 直接跳过该行程
                                self.schedule_set()
                    else:
                        # * 对于其他类型schedule 判断是否到达目的地 - 如果没有达到目的地 说明前置行程被取消 直接跳过
                        self.now = self.user_commond_schedule[self.commond_schedule_index]
                        if 'aoi_position' not in self._agent.motion['position'].keys() or self.now.target_id_aoi != self._agent.motion['position']['aoi_position']['aoi_id']:
                            self.schedule_set(True)
                else:
                    # * 基本行程注册
                    if self.base_schedule_index >=0 and self.base_schedule[self.base_schedule_index].time <= self._agent._simulator.time:
                        self.now = self.base_schedule[self.base_schedule_index]
                        if 'aoi_position' in self._agent.motion['position'].keys() and self._agent.motion['position']['aoi_position']['aoi_id'] == self.now.target_id_aoi:
                            # 直接跳过该行程
                            self.schedule_set()
            else:
                if self.now.type.value == ScheduleType.TRIP.value:
                    if self.now.arrived:
                        self.schedule_set()
                    elif self.now.route_failed:
                        self.schedule_set(True)
                elif self.now.type.value == ScheduleType.SHOP.value:
                    if not self.now.arrived:
                        self.now.arrived = True
                    else:
                        self.now.finished = True
                        self.schedule_set()
                elif self.now.type.value == ScheduleType.OTHER.value:
                    self.now.remain -= 1
                    if self.now.remain <= 0:
                        self.schedule_set()
        self.pre_time = now_time

    def schedule_set(self, need_pass:bool=False):
        if not need_pass:
            self.history.append(self.now)
        if self.is_controled:
            if self.commond_schedule_index >= len(self.user_commond_schedule)-1:
                # * 已完成用户行程
                self.clear_user_schedule()
            else:
                self.commond_schedule_index += 1
        else:
            if self.base_schedule_index < len(self.base_schedule)-1:
                self.base_schedule_index += 1
            else:
                # * 已完成基础行程
                self.base_schedule_index = -1
        self.now = None

    def schedule_init(self):
        '''基于base的行程初始化 - base schedule'''
        for tp in self._agent.base['schedules']:
            trip = tp['trips'][0]
            mode = trip['mode']
            target_aoi_id = trip['end']['aoi_position']['aoi_id']
            target_poi_id = trip['end']['aoi_position']['poi_id']
            time = tp['departure_time']
            description = trip['activity']
            t_init = TripSchedule(target_aoi_id, target_poi_id, "None", mode, time, description)
            self.base_schedule.append(t_init)

        if len(self.base_schedule) > 1:
            now_idx = 0
            for idx in range(len(self.base_schedule)-1):
                # * 排除已完成的schedule
                if self.base_schedule[idx+1].time <= self._agent._simulator.time:
                    self.base_schedule[idx].arrived = True
                    self.history.append(self.base_schedule[idx])
                    now_idx = idx+1
                else:
                    continue
            self.base_schedule_index = now_idx
        else:
            self.base_schedule_index = 0

    def __str__(self) -> str:
        text = '''【Schedule Message】: \n'''
        text += '''[Basic Schedules]: \n'''
        for sche in self.base_schedule:
            text += "       " + sche.__str__()
        if self.is_controled:
            text += '''[User Schedule]: \n'''
            for sche in self.user_commond_schedule:
                text += "       " + sche.__str__()
        text += '''[History Schedule]: \n'''
        for sche in self.history:
            text += "       " + sche.__str__()
        text += f'''[Now Schedule]: \n       {self.now.__str__()}\n'''
        return text