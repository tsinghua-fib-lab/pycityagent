from abc import ABC, abstractclassmethod
from typing import Any, Optional
from action import Action

class ActionStream:
    """
    可以将多个Action聚合在一起构成一个ActionStream, Stream中的Action会顺序执行
    You can collect multiple Actions into a ActionStream, actions in stream will be activated in sequence
    注意: 该部分内容目前没有使用
    """
    def __init__(self, actions:Optional[list[Action]]=[]) -> None:
        self.actions = actions

    def add_actions(self, actions:list[Action]):
        """
        添加Action至当前stream

        Args:
        - actions (list(Action)): a list of action
        """
        self.actions += actions

    def __call__(self) -> Any:
        for action in self.actions:
            action()