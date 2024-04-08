from typing import Any, Optional, Union
from .action import Action
from .citizen_actions.trip import TripAction
from .citizen_actions.shop import ShopAction
from .citizen_actions.converse import ConverseAction
from .citizen_actions.controled import ControledAction
from .citizen_actions.idle import IdleAction

class ActionController:
    """
    Agent行为控制器: 与AppHub(simulator)对接
    Agent Controller: Connect with AppHub and Simulator
    Note: Actions are predefined. By now, user defined actions are not supported
    """
    def __init__(self, agent) -> None:
        self._agent = agent
        self.action_chain = {}
        self.reset_ac()
        self._init_actions()

    async def Run(self):
        agent_state = self._agent.state
        if agent_state in self.action_chain.keys():
            for action in self.action_chain[agent_state]:
                await action.Forward()

    def clear_ac(self):
        """
        清空AC
        """
        self.action_chain.clear()

    def reset_ac(self):
        """
        重置Action Controller
        Reset action controller
        """
        self.action_chain.clear()
        for state in self._agent._st.machine.states.keys():
            self.action_chain[state] = []
        
    def set_ac(self, states:list[str]):
        """
        设置ac
        """
        self.action_chain.clear()
        for state in states:
            self.action_chain[state] = []

    def add_actions(self, state:str, actions:Union[Action, list[Action]]):
        """
        添加Action到目标动作链
        """
        if issubclass(type(actions), Action) or isinstance(actions, Action):
            self.action_chain[state].append(actions)
        else:
            self.action_chain[state] += actions

    def _init_actions(self):
        """
        构建初始化动作链——适用于citizen类型的agent
        """
        self.action_chain['trip'] = [TripAction(self._agent)]
        self.action_chain['shop'] = [ShopAction(self._agent)]
        self.action_chain['conve'] = [ConverseAction(self._agent)]
        self.action_chain['controled'] = [ControledAction(self._agent)]
        self.action_chain['idle'] = [IdleAction(self._agent)]