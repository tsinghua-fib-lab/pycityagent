from abc import ABC, abstractmethod
from typing import Optional, Union, Callable
import PIL.Image as Image
from PIL.Image import Image
import asyncio
import time
from pycitysim.sim import CityClient

from pycityagent.urbanllm import UrbanLLM
from .urbanllm import UrbanLLM
from .brain.brain import Brain
from .hubconnector.hubconnector import HubConnector
from .ac import ActionController
from .cc import CommandController
from .st import StateTransformer

class AgentType:
    """
    Agent类型

    - Citizen = 1, 指城市居民类型agent——行动受城市规则限制
    - Func = 2, 功能型agent——行动规则宽松——本质上模拟器无法感知到Func类型的agent
    """
    Citizen = 1
    Func = 2

class Template:
    """
    The basic template of Agent
    """
    def __init__(self, name, server, type:AgentType, soul:UrbanLLM=None, simulator=None) -> None:
        self._name = name
        self._client = CityClient(server)
        self._type = type
        self._soul = soul
        self._simulator = simulator

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
            type:AgentType,
            soul:UrbanLLM=None, 
            simulator=None
        ) -> None:
        super().__init__(name, server, type, soul, simulator)

        self._hub_connector = None
        """
        HubConnector: 用于和AppHub对接——可以通过Agent.connectToHub进行绑定
        HubConnector: the connection between agent and AppHub, you can use 'Agent.connectToHub' to create the connection
        """

        self._brain = Brain(self)
        """
        Agent的大脑
        The Agent's Brain
        """

        self._cc = CommandController(self)
        """
        Agent的命令控制器
        The Agent's CommondController
        """

        self._st = StateTransformer()
        """
        与Agent关联的状态转移器
        The related StateTransformer
        """

        self._ac = ActionController(self)
        """
        Agent的行为控制器
        The Agent's ActionController
        """

        self._step_with_action = True
        """
        Step函数是否包含action执行 —— 当有自定义action需求(特指包含没有指定source的Action)时可置该选项为False并通过自定义方法执行action操作
        """
    
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

    def set_streetview_config(self, config:dict):
        """
        街景感知配置
        - engine: baidumap / googlemap
        - mapAK: your baidumap AK (if baidumap)
        - proxy: your googlemap proxy (if googlemap, optional)
        """
        if 'engine' in config:
            if config['engine'] == 'baidumap':
                self.Brain.Sence._engine = config['engine']
                if 'mapAK' in config:
                    self.Brain.Sence._baiduAK = config['mapAK']
                else:
                    print("ERROR: Please Provide a baidumap AK")
            elif config['engine'] == 'googlemap':
                self.Brain.Sence._engine = config['engine']
                if 'proxy' in config:
                    self.Brain.Sence._googleProxy = config['proxy']
                else:
                    print("ERROR: Please provide a googlemap proxy")
            else:
                print("ERROR: Wrong engine, only baidumap / googlemap are available")
        else:
            print("ERROR: Please provide a streetview engine, baidumap / googlemap")
    
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

    def set_step_with_action(self, flag:bool = None):
        """
        默认情况置反step_with_action属性: 即True->False, False->True
        否则根据传入的flag进行设置
        """
        if flag != None:
            self._step_with_action = flag
        else:
            self._step_with_action = not self._step_with_action
        

    def sence_config(self, sence_content:Optional[list]=None, sence_radius:int=None):
        '''
        感知配置

        Args:
        - config: 配置选项——包含需要感知的数据类型
            - time: 时间
            - poi: 感兴趣地点
            - position: 可达地点
            - lane: 周围道路
            - person: 周围活动person
            - streetview: 街景
            - user_message: 用户交互信息
            - agent_message: 智能体交互信息
        '''
        if sence_content != None:
            self._brain._sence.set_sence(sence_content)
        if sence_radius != None:
            self._brain._sence.set_sence_radius(sence_radius)

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
        """
        pass
    
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
    def state(self):
        """The state of the Agent"""
        return self._st.machine.state
    
    @property
    def StateTransformer(self):
        """The StateTransformer of the Agent"""
        return self._st

    @property
    def Hub(self):
        """The connected AppHub"""
        return self._hub_connector
    
    @property
    def CommandController(self):
        """The command controller"""
        return self._cc