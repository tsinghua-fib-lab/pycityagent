from typing import Any, Optional
from abc import ABC, abstractmethod
from enum import Enum
import json
from collections import defaultdict
from .brainfc import BrainFunction
from .scheduler import Scheduler
from .persistence.spatial import spacialPersistence
from .retrive.social import *
from .reason.shop import *
from .reason.trip import *
from .reason.user import *
from .reason.social import *

BASE_CONVERSE_DIALOG = [
        {'role': 'system', 'content': '你是一个对话机器人，你将基于背景信息进行角色扮演并做出拟人的, 符合角色逻辑的回答(你的回答应该尽量口语化且与角色的性格特征相符)'},
        {'role': 'system', 'content': '你的回复内容应该被严格限制在角色信息之内, 如果你认为角色无法做出有效回复, 可以从该角色的视角出发表达自己的不足, 例如: 抱歉, 我暂时不知道你所说的内容'},
        {'role': 'system', 'content': '注意: 每次回复前, 你应该根据你们的对话内容进行判断该段对话是否可以结束或无回复必要(例如对方已经说了再见), 如是请输出Finished, 否则请正常回复'}
    ]
"""
Agent对话前置system role dialog
The basic system role dialog used for converse
"""

class MemoryType:
    """
    Enum类: 判断记忆类型
    Enum class: memory type

    LongTermMemory (LTM): 长时记忆的存储
    Working Memory (WM): 当前工作记忆的存储
    """
    LTM = 1
    WM = 2

class MemoryRetrive:
    """
    用于从LTM中获取对应信息
    LTM retrive: get information from LTM

    Args:
    - source (str): the name of source LTM
    - out (str): the output name of retrived information
    - user_func (function): the defined function used for retriving
    """
    def __init__(self, source:str, out:str, user_func) -> None:
        self.source = source
        self.out = out
        self.user_func = user_func

class MemoryReason:
    """
    基于WM的记忆推理与生成, 可以添加MemoryRetrive模块以获取关联信息
    Memory Reason: reason new information from WK, your can add a list of MemoryRetrive to get related information

    Args:
    - out (str): the output name of memory reason
    - user_func (function): the defined function used for reasoning
    - retrivees (Optional[list[MemoryRetrive]]): a list of MemoryRetrive block that help to get related information from LTM
    """
    def __init__(self, out:str, user_func, retrives:Optional[list[MemoryRetrive]]=None) -> None:
        self.out = out
        self.user_func = user_func
        self.retrives = retrives

class MemoryPersistence:
    """
    记忆持久化: 将WM中的内容存储到LTM中
    Memory Persistence: store memory from WM to LTM

    Args:
    - target (str): the name of target LTM
    - user_func (function): the defined function used for persistence
    """
    def __init__(self, target: str, user_func) -> None:
        self.target = target  # 指代的是目标记忆体
        self.user_func = user_func  # 用户注入的可执行函数

class MemoryController:
    """
    记忆管理器
    Memory Controller
    """
    def __init__(self, agent, memory_config:dict=None) -> None:
        self._agent = agent
        self._soul = agent._soul
        if memory_config != None:
            pass
        else:
            self._wm = WorkingMemory(agent)
            self._spatial = SpatialMemory(agent)
            self._social = SocialMemory(agent)

    async def Forward(self):
        """
        记忆模块主工作流
        Main working flow of Memory
        """
        await self._wm.senceReceive(self._agent.Brain.Sence.sence_buffer)
        await self._wm.Forward()

    def reset_Memory(self):
        """
        重置记忆内容
        Reset Memory
        Notice: by now, this function only reset all social related information, including unhandled messages and working messages
        """
        self._social.unhandle = []
        self._social.still = []

    @property
    def Spatial(self):
        """
        空间记忆 (LTM)
        Spatial Memory (LTM)
        """
        return self._spatial
    
    @property
    def Social(self):
        """
        社交记忆 (LTM)
        Social Memory (LTM)
        """
        return self._social
    
    @property
    def Working(self):
        """
        工作记忆 (WM)
        Working Memory (WM)
        """
        return self._wm
    
    @property
    def Soul(self):
        return self._soul
    
    @property 
    def Hub(self):
        return self._agent._hub

class Memory(BrainFunction):
    """
    记忆模板类
    The template class of Memory: defined as a BrainFunction
    """
    def __init__(self, agent, type:MemoryType) -> None:
        super().__init__(agent)
        self.type = type
    
    def Forward(self, x):
        """
        数据工作流
        The data workflow
        """

    def MemorySave(self):
        """
        记忆存储
        Save Memory
        """

    def MemoryLoad(self, x):
        """
        记忆恢复
        Load Memory
        """

class WorkingMemory(Memory):
    """
    当前工作记忆
    Working Memory
    """
    def __init__(self, agent) -> None:
        super().__init__(agent, MemoryType.WM)
        self.sence = None
        """
        用于存储感知内容
        Store the sence content
        """
        self.scheduler = Scheduler(agent)
        """
        关联的规划器
        The related Scheduler
        """
        self.Reason = {}
        """
        用于存储Reason结果的buffer: key值为MemoryReason.out
        """

        # * agent social
        self.agent_converse_buffer = defaultdict(lambda: BASE_CONVERSE_DIALOG+[
            {'role': 'system', 'content': f'''[角色基本信息]: {self._agent.Image.get_profile()}'''}, 
            {'role': 'system', 'content': f'''[角色的空间知识]: {self._agent.Brain.Memory.Spatial.to_dialog_str()}'''},
            {'role': 'system', 'content': f'''[角色的社交关系]: {self._agent.Brain.Memory.Social.to_dialog_str()}'''}
        ])
        """
        存储当前仍未结束的对话内容
        Store the content of working conversation
        """

        self.hello_dialog = [
            {'role': 'system', 'content': '你将基于用户提供的基本信息以及周围人物信息, 预测用户当前对哪个人最感兴趣, 是否会和该人物进行对话, 以及进行对话的理由'},
            {'role': 'system', 'content': '其中基本信息包含用户的个人信息, 周围人物信息包含他人的基本信息以及用户对该人物的了解'},
            {'role': 'system', 'content': '你只需要提供一个整数(该整数为对应人物的id)即可(请勿包含其他冗余信息)'},
            {'role': 'system', 'content': '''你的回答需要严格按照以下格式给出(请勿包含其他冗余信息):
            {"id": 感兴趣人物的id, "conve": 是否进行对话, 可选集合为[是, 否], 'explaination': 进行或不进行对话的理由}'''}
        ]
        """
        Agent主动打招呼的system role dialog
        The basic system role dialog used for saying hello
        """

        self.msg_agent_unhandle = {}  # dict of unhandle agent messages
        """
        存储未处理消息
        Store unhandled agent messages
        """

        self.msg_agent_still = {}  # still on converse person_id
        """
        存储正在进行对话的person_id
        Store the target person_id of conversations that still working
        """

        # * user message related
        self.current_target = None
        """
        当前的目标
        Agent's current target
        """
        self.has_user_command = False
        """
        是否有用户指令
        Whether there have user commond
        """
        self.user_converse_buffer = BASE_CONVERSE_DIALOG+[{'role': 'system', 'content': self._agent.Image.get_profile()}]
        """
        存储用户对话信息
        Store user conversation content
        """
        self.understanding_prompt = [
            {'role': 'system', 'content': '请你根据用户的输入内容，判断用户向你发起对话的用意并返回结果，返回的结果只能是[对话]或[控制]中的一个'},
            {'role': 'system', 'content': '其中[对话]表示用户只是想与你进行常规对话；[控制]表示用户想要控制你的行动'},
            {'role': 'system', 'content': '例如用户输入: 你好, 你的返回结果为: 对话'},
            {'role': 'system', 'content': '例如用户输入: 你现在立刻去附近买菜, 你的返回结果为: 控制'}
        ]
        """
        用于判断user对话意图的基础system role dialog
        The basic system role dialog used for interpreting converse intent, converse or commond
        """

        self.msg_user_unhandle = []  # unhandle user messages
        """
        存储未处理的用户消息
        Store unhandled user messages
        """
        self.msg_user_processing = []  # processing user messages
        """
        存储正在处理的用户信息
        Store working user messages
        """

        # * config
        self.enable_user_interaction = True
        self.enable_economy = True
        self.enable_social = True

        # * 信息提取
        self.retrive = {
            'getfamilier': MemoryRetrive('Social', 'familiers', getfamilier)
        }
        """
        记忆索引模块集合
        The collection of MemoryRetrive blocks
            - key (str(MemoryRetrive.user_func))
            - value (MemoryRetrive)
        """

        # * reason - 推理/判断功能
        self.reason = {
            'idle': [
                MemoryReason("hasUserControl", hasUserControl),
                MemoryReason("startTrip", startTrip),
                MemoryReason("agent_message_handle_resp", handleConve, [self.retrive['getfamilier']]),
                MemoryReason("startConve", startConve),
                MemoryReason("startShop", startShop)
            ],
            'trip': [
                MemoryReason("hasUserControl", hasUserControl),
                MemoryReason("routeFailed", routeFailed),
                MemoryReason("tripArrived", tripArrived)
            ],
            'conve': [
                MemoryReason("hasUserControl", hasUserControl),
                MemoryReason("agent_message_handle_resp", handleConve, [self.retrive['getfamilier']]),
                MemoryReason("endConve", endConve),
            ],
            'shop': [
                 MemoryReason("hasUserControl", hasUserControl),
                 MemoryReason("endShop", endShop)
            ],
            'controled': [
                MemoryReason("endUserControl", endUserControl)
            ]
        }
        """
        记忆推理模块集合
        The collection of MemoryReason blocks
            - key (str): state
            - value (list[MemoryReason])
        Notice: 根据Agent当前状态执行对应列表中的MemoryReason. Execute those corresponding MemoryReason blocks based on Agent's state
        """

        # * persistence - 记忆持久化
        self.persistence = [
            MemoryPersistence('Spatial', spacialPersistence)
        ]
        """
        记忆持久化模块集合
        The collection of MemoryPersistence blocks
        """

    async def Forward(self):
        """
        WM主工作流
        The main workflow of WM
            - Reason
            - Persistence
            - (if need) Schedule
        """
        await self.runReason()
        await self.runPersistence()
        if self.has_user_command:
            ret = await self.scheduler.schedule(self.current_target)
            if ret != 0:
                self.Reason['hasUserControl'] = False
                self._agent.Hub.Update([AgentMessage(self._agent.Hub._agent_id, int(time.time()*1000), '抱歉，行程规划失败，请重试', None, None)])
            self.has_user_command = False
        await self.scheduler.schedule_forward()
        if not self.scheduler.is_controled:
            self.current_target = None

    async def senceReceive(self, sence):
        """
        获取Sence结果的接口
        The interface used for receiving sence contents
        """
        self.sence = sence
        # * social message
        social_message = sence['social_messages']
        for message in social_message:
            print(message)
            from_id = message['from']
            content = message['message']
            if from_id in self.msg_agent_unhandle.keys():
                self.msg_agent_unhandle[from_id] += [{
                    'role': 'user',
                    'content': content
                }]
            else:
                self.msg_agent_unhandle[from_id] = [{
                    'role': 'user',
                    'content': content
                }]
        # * user message
        self.msg_user_unhandle = sence['user_messages']

    async def runReason(self):
        '''推理模块执行'''
        reason_line = self.reason[self._agent.state]
        for reason in reason_line:
            if reason.retrives == None:
                self.Reason[reason.out] = await reason.user_func(self)
            else:
                retrives = {}
                for retrive in reason.retrives:
                    retrives[retrive.out] = await retrive.user_func(getattr(self.LTM, retrive.source))
                self.Reason[reason.out] = await reason.user_func(self, retrives)

    async def runPersistence(self):
        '''持久化模块执行'''
        for persis in self.persistence:
            mem = getattr(self._agent.Brain.Memory, persis.target)
            await persis.user_func(self, mem)

    def set_user_converse_background(self):
        self.user_converse_buffer[2]['content'] = self._agent.Image.get_profile()

    @property
    def LTM(self):
        return self._agent.Brain.Memory

class SpatialMemory(Memory):
    """
    空间记忆 (LTM)
    SpatialMemory (LTM)

    空间记忆以location_node为基本组织单位, 每一个node被组织为一个dict, 包含以下属性
    The based unit of Spatial Memory is location_node, each node is presented as a dict, including following attributes:
        - id (int): the id of target location, '700426179' for instance
        - name (str): the name of target location, '清华大学' for instance
        - category (str): the category of target location, '教育学校' for instance
        - aoi_id (int): the related AOI's id, '500000011' for instance
        - relation (str): the relation between Agent and the location, '我在这里任职' for instance
    """
    def __init__(self, agent) -> None:
        super().__init__(agent, MemoryType.LTM)
        self.constant = []
        """
        以列表形式存储的空间记忆: 基于文件载入的
        Spatial Memory in list: based on the MemoryLoad
        list[location_node]
        """
        self.sence = []
        """
        以列表形式存储的空间记忆: 基于Sence结果
        Spatial Memory in list: based on the Sence
        list[location_node]
        """
        self.spatial_dict = {}
        """
        以字典形式存储的空间记忆: key为id, value未node
        Spatial Memory in dict collection
            - key: id
            - value: location_node
        """

    def Forward(self, x:list, to_constant:bool = False):
        """
        将输入内容x存储到记忆中
        Store x to spatial memory

        Args:
        - x (list): spatial nodes in list
        - to_constant (bool): whether store to constant, if False, only store to sence buffer, default False
        """
        for loc in x:
            self.spatial_dict[loc['id']] = loc
        self.sence += x
        if to_constant:
            self.constant += x

    def MemoryLoad(self, file_name:str):
        """
        基于文件载入空间记忆
        Load Spatial Memory based on static file

        Args:
        - file_name (str): the path of file name
        """
        try:
            with open(file_name, 'r') as f:
                data = json.load(f)
                for loc in data:
                    self.spatial_dict[loc['id']] = loc
                self.constant += data
                print("Load Succes.")
        except:
            print("Can't load spatial knowledge.")

    def MemorySave(self, file_name:str):
        """
        将空间记忆存储为文件
        Store Spatial Memory to file
        Notice: only stores those in constant

        Args:
        - file_name (str): the file name
        """
        with open(file_name, 'w') as f:
            json.dumps(self.constant, f)

    def to_dialog_str(self):
        """
        将空间信息转换为LLM可理解的文本
        Transfer Spatial Memory to LLM unstandable text
        """
        temp = self.constant + self.sence
        return json.dumps(temp, indent=0)

class SocialMemory(Memory):
    """
    社交记忆 (LTM)
    Social Memory (LTM)

    社交记忆以person_node为基本组织单位, 每一个node被组织为一个dict, 包含以下属性
    The based unit of Social Memory is person_node, each node is presented as a dict, including following attributes:
        - id (int): person_id, '8' for instance
        - name (str): the name of person, '张三' for instance
        - relation (str): the relation between Agent and the target person, '亲密朋友' for instance
        - learned (str): the information that Agent learned about the target person, '他最近在学习AI' for instance
    """
    def __init__(self, agent) -> None:
        super().__init__(agent, MemoryType.LTM)
        self.familiers = []
        """
        以列表形式存储社交记忆
        The Social Memory in list collection
        list[person_node]
        """
        self.familiers_dict = {}
        """
        以字典形式存储的社交记忆
        The Social Memory in dict collection
            - key: person_id
            - value: person node
        """

    def MemoryLoad(self, file_name:str):
        """
        基于文件的社交记忆加载
        Load Social Memory based on file

        Args:
        - file_name (str): the path of file
        """
        with open(file_name, 'r') as f:
            persons = json.load(f)
            for person in persons:
                self.familiers_dict[person['id']] = person
            self.familiers += persons

    def MemorySave(self, file_name:str):
        """
        将社交记忆存储为文件
        Store Social Memory to file

        Args:
        - file_name (str): the path of file
        """
        with open(file_name, 'w') as f:
            json.dumps(self.familiers, f)

    def to_dialog_str(self):
        """
        将社交记忆转化为LLM可理解的文本
        Transfer the Social Memory to LLM understandable text
        """
        return json.dumps(self.familiers, indent=0)