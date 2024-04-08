from typing import Any
from .idle import *
from .shop import *
from .trip import *
from .conve import *
from .user import *

class Command:
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

class CommandController:
    """
    Commond控制器模组: 连接Brain以及StateTranformer
    Commond Controller module: Used to connect the Brain module and StateTransformer module
    """
    def __init__(self, agent) -> None:
        '''默认初始化'''
        # TODO: config配置
        self._agent = agent
        self._brain = agent._brain
        self.command_line = {}
        """
        默认控制序列: 与state关联的BrainCommond集合
        Control Hub: connect the state with a BrainCommond collection
        Type: dict[str, list[BrainCommond]]
        Default:
            - idle: [whetherUserControl, whetherGoTrip, whetherGoShop, whetherGoConverse]
            - trip: [whetherUserControl, whetherRouteFailed, whetherTripArrived]
            - shop: [whetherUserControl, whetherShopFinished]
            - conve: [whetherUserControl, whetherStopConverse]
            - controled: [whetherEndControl]
        """

        self.command_line['idle'] = [
            Command('gousercontrol', whetherUserControl),
            Command('gotrip', whetherGoTrip),
            Command('goshop', whetherGoShop),
            Command('goconverse', whetherGoConverse)
        ]
        self.command_line['trip'] = [
            Command('gousercontrol', whetherUserControl),
            Command('routefailed', whetherRouteFailed),
            Command('arrived', whetherTripArrived)
        ]
        self.command_line['shop'] = [
            Command('gousercontrol', whetherUserControl),
            Command('shopdone', whetherShopFinished)
        ]
        self.command_line['conve'] = [
            Command('gousercontrol', whetherUserControl),
            Command('convedone', whetherStopConverse)
        ]
        self.command_line['controled'] = [
            Command('controlback', whetherEndControl)
        ]

    def reset_cc(self):
        """
        重置命令控制器
        """
        self.command_line = {}

    def insert_command(self, target_state:list[str], command:Command):
        """
        插入指令
        Insert Commond: This function will insert the commond to those control sequences show in target_state

        Args:
        - target_state (list[str]): the list of state names
        - commond (Comond): the commond to be inserted
        """
        for target in target_state:
            if target in self.command_line.keys():
                self.command_line[target].append(command)
            else:
                self.command_line[target] = [command]

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
        if self._agent.state not in self.command_line.keys():
            print(f"No commond control line match with current state: {self._agent.state}")
        control_line = self.command_line[self._agent.state]  # 获取agent状态对应的控制链
        for control in control_line:
            result = await control.user_func(self._agent.Brain.Memory.Working)
            if result:
                return control.target
        return 'nothing'