from typing import Optional
import json
from abc import ABC, abstractclassmethod


class Image:
    """
    Image模块: 智能体画像
    Agent's Image module: Defines the uniqueness of Agent
    """
    def __init__(self, agent) -> None:
        self._agent = agent
        self.scratch = Scratch()
    
    def get_profile(self):
        """
        获取Agent的Scratch Profile信息
        Get the Scratch Profile message

        Returns:
        - (str)
        """
        return self.scratch.get_profile_content()
    
    def load_scratch(self, scratch_file:str):
        """
        加载基于文件的Profile加载
        Load Profile based on file

        Args:
        - scratch_file (str): the path of scratch_file
        """
        self.scratch.load(scratch_file)

class CitizenImage(Image):
    """
    Agent Image模块: 用户画像控制
    Agent's Image module: Defines the uniqueness of Agent
    """
    def __init__(self, agent, scratch_file:str=None, selfie:bool=False) -> None:
        self._agent = agent
        self.scratch = CitizenScratch()
        """
        Agent的Scratch信息: 用于描述Agent的基本属性
        Scratch: Used to describe the basic info of Agent
        - name (str): the name of Agent
        - age (int): the age of Agent
        - education (str): the education level, ['低等教育水平', '中等教育水平', '高等教育水平']
        - gender (str): the gender of Agent, ['男', '女']
        - consumption (str): the consumption level , ['低等消费水平', '中等消费水平', '高等消费水平']
        - innate (str): the innate of Agent, '乐观积极' for instance
        - learned (str): the learned info of Agent, '我是一名教师, 就职于xxx' for instance
        - currently (str): the currently plan of Agent, '写一篇关于社会科学的研究报告' for instance
        - lifestyle (str): the lifestyle of Agent, '早上7点起床, 晚上11点睡觉' for instance
        """
        self.selfie = None
        """
        Agent自画像
        Selfie of Agent
        Not implement yet!!!
        """
        profile = self._agent.base['profile']
        if scratch_file != None:
            self.scratch.load(scratch_file)
        else:
            self.scratch.name = self._agent._name
            self.scratch.age = profile['age']
            education = profile['education']
            if education < 3:
                self.scratch.education = '低等教育水平'
            elif education < 5:
                self.scratch.education = '中等教育水平'
            else:
                self.scratch.education = '高等教育水平'
            if profile['gender'] == 1:
                self.scratch.gender = '男'
            else:
                self.scratch.gender = '女'
            consumption = profile['consumption']
            if consumption < 3:
                self.scratch.consumption = '低等消费水平'
            elif consumption < 5:
                self.scratch.consumption = '高等消费水平'
            else:
                self.scratch.consumption = '高等消费水平'
        if selfie:
            # TODO: 补充自拍
            pass

    def load_selfie(self, selfie_file:str):
        """
        基于图像的Selfie加载
        Load Selfie based on selfie file
        Not implemented yet!!!

        Args:
        - selfie_file (str): the path of selfie_file
        """
        print("Not Implemented")

class Scratch:
    def __init__(self, scratch: Optional[dict]=None) -> None:
        if scratch != None:
            self.forward(scratch)

    def forward(self, x:dict):
        """Scratch记忆更新"""
        for k in x.keys():
            self.__dict__[k] = x[k]

    def save(self, output_path:str):
        """Scratch记忆持久化"""
        with open(output_path, 'w') as f:
            json.dumps(self.__dict__, f, 4)
    
    def load(self, x:str):
        """Scratch记忆恢复"""
        with open(x, 'r') as f:
            json_str = f.read()
            scratch = json.loads(json_str)
            self.forward(scratch)

    def get_profile_content(self):
        text = ""
        for attr_name, attr_value in self.__dict__.items():
            text += f"{attr_name}: {attr_value}\n"
        return text

class CitizenScratch(Scratch):
    def __init__(self, scratch:Optional[dict]=None) -> None:
        super().__init__(scratch=scratch)
        self.name = None
        self.age = None
        self.education = None
        self.gender = None
        self.consumption = None
        self.innate = ''
        self.learned = ''
        self.currently = ''
        self.lifestyle = ''
    
    def get_str_lifestyle(self):
        return self.lifestyle
    
    def get_str_firstname(self):
        return self.first_name
    
    def get_profile_content(self):
        text = ''''''
        text += f'姓名: {self.name}\n'
        text += f'年龄: {self.age}\n'
        text += f'性别: {self.gender}\n'
        text += f'受教育水平: {self.education}\n'
        text += f'消费能力: {self.consumption}\n'
        text += f'性格特点: {self.innate}\n'
        text += f'爱好与习惯: {self.learned}\n'
        text += f'近期状态: {self.currently}\n'
        text += f'生活习惯: {self.lifestyle}\n'
        return text

    def __str__(self):
        return str(self.__dict__)