from abc import ABC, abstractmethod
from typing import Optional, Union
import PIL.Image as Image
from PIL.Image import Image
import asyncio
import time
from pycitysim.sim import CityClient

from pycityagent.urbanllm import UrbanLLM
from .urbanllm import UrbanLLM
from .brain.brain import Brain
from .hubconnector.hubconnector import HubConnector
from .image.image import AgentImage
from .ac.ac import ActionController
from .cc.cc import CommondController
from .st.st import StateTransformer


class Template:
    """
    The basic template of Agent
    """
    def __init__(self, name, server, soul:UrbanLLM=None, simulator=None, id:int=None) -> None:
        self.agent_name = name
        self._client = CityClient(server)
        self._soul = soul
        self._simulator = simulator
        self._id = id

    def add_soul(self, llm_engine:UrbanLLM):
        """
        为Agent添加soul(UrbanLLM)
        Add soul for Agent

        Args:
        - llm_engine (UrbanLLM): the soul
        """
        self._soul = llm_engine

    def add_simulator(self, simulator):
        """
        添加关联模拟器
        Add related simulator

        Args:
        - simulator (Simulator): the Simulator object
        """
        self._simulator = simulator

    @abstractmethod
    def Step(self):
        """模拟器执行接口"""

class Agent(Template):
    """
    Agent
    """
    def __init__(
            self, 
            name:str, 
            server:str, 
            soul:UrbanLLM=None, 
            simulator=None, 
            id:int=None, 
            base=None,
            motion=None,
            scratch_file:str=None,
            selfie:bool = False,
            connect_to_hub:bool=False,
            hub_url:str=None,
            app_id:int=None,
            app_secret:str=None,
            profile_img:str=None
        ) -> None:
        super().__init__(name, server, soul, simulator, id)
        self.base = base
        """
        Agent/Person的基本属性, Agent指被代理的Person, Person指模拟器中的背景人
        The base attributes of Agent/Person. Agent is the Person being represented. Persons are background persons in simulator
        - https://cityproto.sim.fiblab.net/#city.agent.v2.Agent
        """
        self.motion = motion
        """
        Agent/Person的运动信息
        The motion information of Agent/Person
        - https://cityproto.sim.fiblab.net/#city.agent.v2.AgentMotion
        """
        if connect_to_hub:
            self._hub_connector = HubConnector(
                hub_url=hub_url,
                app_id=app_id,
                app_secret=app_secret,
                agent=self,
                profile_img=profile_img
            )
        else:
            self._hub_connector = None
        self._image = AgentImage(self, scratch_file, selfie)
        """
        Agent画像
        The Agent's Image
        """
        self._brain = Brain(self)
        """
        Agent的大脑
        The Agent's Brain
        """
        self._ac = ActionController(self)
        """
        Agent的行为控制器
        The Agent's ActionController
        """
        self._cc = CommondController(self)
        """
        Agent的命令控制器
        The Agent's CommondController
        """
        self._st = StateTransformer()
        """
        与Agent关联的状态转移器
        The related StateTransformer
        """
        # * 默认trip构建
        self.Scheduler.schedule_init()
    
    def ConnectToHub(self, config:dict):
        """
        与AppHub构建连接
        Connect to AppHub

        Args:
        - config (dict): the config dict of AppHub
        """
        profile_img = None
        if 'profile_image' in config.keys():
            profile_img = config['profile_image']
        self._hub_connector = HubConnector(
            hub_url=config['hub_url'],
            app_id=config['app_id'],
            app_secret=config['app_secret'],
            agent=self,
            profile_img=profile_img
        )
    
    def enable_streetview(self):
        """
        开启街景相关功能
        Enable Streetview function
        """
        self._brain.Sence.enable_streeview = True

    def disable_streetview(self):
        """
        关闭街景相关功能
        Disable Streetview function
        """
        self._brain.Sence.enable_streeview = False

    def enable_user_interaction(self):
        """
        开启用户交互功能(即在OpenCity控制台中与Agent进行交互)
        Enable User Interaction function. The User Interaction function is the ability to interact with the related agent in OpenCity website console.
        """
        self._brain.Memory.Working.enable_user_interaction = True

    def disable_user_interaction(self):
        """
        关闭用户交互功能
        Disable User Interaction function
        """
        self._brain.Memory.Working.enable_user_interaction = False

    def enable_economy_behavior(self):
        """
        开启经济模拟相关功能(例如购物)
        Enable Economy function. Shopping for instance.
        """
        self.Brain.Memory.Working.enable_economy = True

    def disable_economy_behavior(self):
        """
        关闭经济模拟相关功能
        Disable Economy function
        """
        self.Brain.Memory.Working.enable_economy = False

    def enable_social_behavior(self):
        """
        开启社交相关功能
        Enable Social function
        """
        self.Brain.Memory.Working.enable_social = True

    def diable_social_behavior(self):
        """
        关闭社交相关功能
        Disable Social function
        """
        self.Brain.Memory.Working.enable_social = False

    async def Pause(self):
        """
        暂停Agent行为使Agent进入'pause'状态
        Pause the Agent, making the agent 'pause'

        """
        req = {'person_id': self.base['id'], 'schedules': []}
        await self._client.person_service.SetSchedule(req)
        self.Scheduler.unset_schedule()
        self._st.trigger('pause')

    async def Active(self):
        """
        恢复Agent行为
        Recover from 'pause'
        """
        self._st.pause_back()

    async def Run(self, round:int=1, interval:int=1, log:bool=True):
        """
        Agent执行入口
        The Agent Run entrance

        Args:
        - round (int): 执行步数. The steps to run.
        - interval (int): 步与步之间的执行间隔, 单位秒. The interval between steps, second.
        - log (bool): 是否输出log信息, 默认为True. Whether console log message, default: True
        """
        if self._soul == None:
            print("Do not add soul yet. Try add_soul(UrbanLLM)")
        await self.Step(log)
        for i in range(0, round-1):
            time.sleep(interval)
            await self.Step(log)

    async def Step(self, log:bool):
        """
        单步Agent执行流
        Single step entrance
        (Not recommended, use Run() method)

        Args:
        - log (bool): 是否输出log信息. Whether console log message
        """
        if self.state != 'paused':
            # * 1. 模拟器时间更新
            await self._simulator.GetTime()
            # * 2. 拉取Agent最新状态
            resp = await self._client.person_service.GetPerson({'person_id':self._id})
            self.base = resp['base']
            self.motion = resp['motion']
            # * 3. Brain工作流
            await self._brain.Run()
            # * 4. Commond Controller工作流
            commond = await self._cc.Run()
            # * 5. State Transformer工作流
            self._st.trigger(commond)
            # * 6. Action Controller工作流
            await self._ac.Run()
        if log:
            print(f"---------------------- SIM TIME: {self._simulator.time} ----------------------")
            self.show_yourself()
    
    def show_yourself(self):
        """
        Log信息输出
        Pring log message
        """
        print(f"【State Message】: {self.state}")
        motion_message = ''''''
        motion_message += f'''行为状态: {self.motion['status']}, '''
        if 'lane_position' in self.motion['position'].keys():
            motion_message += f'''位置信息: lane-{self.motion['position']['lane_position']['lane_id']}'''
        else:
            motion_message += f'''位置信息: aoi-{self.motion['position']['aoi_position']['aoi_id']}'''
        motion_message += f'''-[x: {self.motion['position']['xy_position']['x']}, y: {self.motion['position']['xy_position']['y']}]'''
        print(f'【Simulator Motion Message】: \n{motion_message}')
        print(self.Scheduler)
    
    @property
    def Image(self):
        """The Agent's Image"""
        return self._image
    
    @property
    def Soul(self):
        """The Agent's Soul(UrbanLLM)"""
        return self._soul
    
    @property
    def Brain(self):
        """The Agent's Brain"""
        return self._brain
    
    @property
    def ActionController(self):
        """The Agents's ActionController"""
        return self._ac

    @property
    def Scheduler(self):
        """The Agent's Scheduler"""
        return self._brain.Memory.Working.scheduler
    
    @property
    def state(self):
        """The state of the Agent"""
        return self._st.state
    
    @property
    def StateTransformer(self):
        """The StateTransformer of the Agent"""
        return self._st

    @property
    def Hub(self):
        """The connected AppHub"""
        return self._hub_connector