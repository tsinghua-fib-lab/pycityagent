from typing import Any
from .idle import *
from .shop import *
from .trip import *
from .conve import *
from .user import *

class Commond:
    """
    BrainCommond: 即脑部发出的指令; The commond from Agent's Brain

    Args:
    - target (str): 即指令目标(状态转移指令). The commond target(state transformer)
    - user_func (func):
        - 自定义函数, 返回结果为bool类型, 如果返回True, 则表示执行target指令. Self-defined function, the return type is bool, if this function returns 'True', then forward the target commond.
    """
    def __init__(self, target:str, user_func) -> None:
        self.target = target
        self.user_func = user_func

class CommondController:
    """
    Commond控制器模组: 连接Brain以及StateTranformer
    Commond Controller module: Used to connect the Brain module and StateTransformer module
    """
    def __init__(self, agent, config=None) -> None:
        '''默认初始化'''
        # TODO: config配置
        self._agent = agent
        self._brain = agent._brain
        self.commond_control = {}
        """
        控制序列: 与state关联的BrainCommond集合
        Control Hub: connect the state with a BrainCommond collection
        Type: dict[str, list[BrainCommond]]
        Default:
            - idle: [whetherUserControl, whetherGoTrip, whetherGoShop, whetherGoConverse]
            - trip: [whetherUserControl, whetherRouteFailed, whetherTripArrived]
            - shop: [whetherUserControl, whetherShopFinished]
            - conve: [whetherUserControl, whetherStopConverse]
            - controled: [whetherEndControl]
        """
        if config != None:
            pass
        else:
            self.commond_control['idle'] = [
                Commond('gousercontrol', whetherUserControl),
                Commond('gotrip', whetherGoTrip),
                Commond('goshop', whetherGoShop),
                Commond('goconverse', whetherGoConverse)
            ]
            self.commond_control['trip'] = [
                Commond('gousercontrol', whetherUserControl),
                Commond('routefailed', whetherRouteFailed),
                Commond('arrived', whetherTripArrived)
            ]
            self.commond_control['shop'] = [
                Commond('gousercontrol', whetherUserControl),
                Commond('shopdone', whetherShopFinished)
            ]
            self.commond_control['conve'] = [
                Commond('gousercontrol', whetherUserControl),
                Commond('convedone', whetherStopConverse)
            ]
            self.commond_control['controled'] = [
                Commond('controlback', whetherEndControl)
            ]

    def insertCommond(self, target_state:list[str], commond:Commond):
        """
        插入指令
        Insert Commond: This function will insert the commond to those control sequences show in target_state

        Args:
        - target_state (list[str]): the list of state names
        - commond (Comond): the commond to be inserted
        """
        for target in target_state:
            if target in self.commond_control.keys():
                self.commond_control.append(commond)
            else:
                self.commond_control[target] = [commond]

    async def Run(self):
        """
        AC主执行函数
        The main function of AC
        Note: By now, AC do not support priority invoke. You can manipulate the sequnce of Commond to create fake priority

        Basic Logic: 
            - Based on the current state of Agent, AC invoke those functions in sequence
            - If there is a 'True' of function, returns the target commond
            - Else, return 'nothing' commond
        """
        if self._agent.state not in self.commond_control.keys():
            print(f"No commond control line match with current state: {self._agent.state}")
        control_line = self.commond_control[self._agent.state]  # 获取agent状态对应的控制链
        for control in control_line:
            result = await control.user_func(self._agent.Brain.Memory.Working)
            if result:
                return control.target
        return 'nothing'