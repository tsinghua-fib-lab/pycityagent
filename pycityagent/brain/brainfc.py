class BrainFunction:
    """
    大脑功能模块模板类
    The template class of brain function
    """
    def __init__(self, agent) -> None:
        self._agent = agent

    def state_influence(self):
        '''agent state影响接口函数'''