from pycitysim import *
from pycitysim.routing import RoutingClient
from pycitysim.sim import CityClient
from typing import Optional, Union
from datetime import datetime, timedelta
import asyncio
from .agent_citizen import CitizenAgent
from .agent_func import FuncAgent

class SimPerceive:
    """
    模拟器感知
    Simulator Perceive
    """
    def __init__(self, simualtor) -> None:
        self._simulator=simualtor
    
    async def PerceiveAoisByIds(self, ids:Optional[list[int]]):
        """
        Simulator视角下的AOI感知
        Perceive AOI from Simulator

        Args:
        - ids list[int]: list of aoi id

        Returns:
        - https://cityproto.sim.fiblab.net/#city.map.v2.GetAoiResponse
        """
        req = {'aoi_ids': ids}
        resp = await self._simulator._client.aoi_service.GetAoi(req)
        return resp

class Simulator:
    """
    模拟器
    Simulator
    """
    def __init__(self, config) -> None:
        self.config = config
        self._client = CityClient(self.config['simulator']['server'], secure=True)
        self._perceive = SimPerceive(self)
        self.map = map.Map(
            mongo_uri = "mongodb://sim:FiblabSim1001@mgo.db.fiblab.tech:8635/",
            mongo_db = "srt",
            mongo_coll = config['map_request']['mongo_coll'],
            cache_dir = config['map_request']['cache_dir'],
        )
        self.routing = RoutingClient(self.config['route_request']['server'], True)
        self.time = 0

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
            for agent in resp.motions:
                if agent.status in status:
                    motions.append(agent)
            resp.motions = motions
            return resp

    async def GetCitizenAgent(self, name:str, id:int):
        """
        获取agent
        Get Agent

        Args:
        - name str: 你为agent取的名字 the name of your agent
        - id int: 即绑定的person的id the id of person that you try to bind with
        
        Returns:
        - CitizenAgent
        """
        await self.GetTime()
        resp = await self._client.person_service.GetPerson({"person_id": id})
        base = resp['base']
        motion = resp['motion']
        agent = CitizenAgent(
            name, 
            self.config['simulator']['server'], 
            simulator=self, 
            id=id, 
            base=base,
            motion=motion
        )
        agent.set_streetview_config(self.config['streetview_request'])
        return agent

    async def GetFuncAgent(self, id:int, name:str):
        """
        获取一个Func Agent模板

        Args:
        - name (str): the name of your agent
        - id (int): the unique id of agent

        Returns:
        - FuncAgent
        """
        agent = FuncAgent(
                    name,
                    id+10000000,
                    self.config['simulator']['server'],
                    simulator=self
                )
        agent.set_streetview_config(self.config['streetview_request'])
        return agent

    def InsertCitizenAgent(self, profile):
        """
        插入agent
        Insert Agent
        Not implemented yet
        """
        print("Not Implemented Yet")
        pass
        
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
        self.time = t_sec['t']
        if format_time:
            current_date = datetime.now().date()
            start_of_day = datetime.combine(current_date, datetime.min.time())
            current_time = start_of_day + timedelta(seconds=t_sec['t'])
            formatted_time = current_time.strftime(format)
            return formatted_time
        else:
            return t_sec['t']

            
    @property
    def Perceive(self):
        """模拟器感知模块"""
        return self._perceive