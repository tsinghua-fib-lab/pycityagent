from pycityagent.urbanllm import UrbanLLM
from .urbanllm import UrbanLLM
from .agent import Agent, AgentType
from .image.image import CitizenImage

class CitizenAgent(Agent):
    """
    Citizen Agent
    城市居民智能体
    """

    def __init__(
            self, 
            name:str, 
            server:str, 
            id:int, 
            soul:UrbanLLM=None, 
            simulator=None, 
            base=None,
            motion=None
        ) -> None:
        super().__init__(name, server, AgentType.Citizen, soul, simulator)
        self._id = id
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

        self._image = CitizenImage(self)
        """
        Agent画像
        The Agent's Image
        """

        self.Scheduler.schedule_init()
        """
        行程初始化
        """

    def Bind(self):
        """
        将智能体绑定到AppHub
        Bind Agent with AppHub
        """
        if self._hub_connector == None:
            print("ERROR: connect with apphub first")
        else:
            self._hub_connector.BindCitizenAgent()


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
    def Scheduler(self):
        """The Agent's Scheduler"""
        return self._brain.Memory.Working.scheduler