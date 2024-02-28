from transitions import Machine
from abc import ABC, abstractmethod

class StateTransformer:
    """
    State Transformer模块: 控制agent状态转移
    The State Transformer module: used to control the transformation of agent's state

    Doc:
    - 基于transitions()构建 https://github.com/tyarkoni/transitions
    - Agent的状态不仅表征着用户当前的行为, 同时也起到了串联/控制Agent行为的功能 
    - 状态信息:
        - idle: 空闲状态
        - trip: 出行状态
        - shop: 购物状态
        - conve: 社交状态
        - paused: 暂停状态
        - controled: 受控状态, 即用户通过OpenCity website console控制Agent
    - 状态转移:
        - idle:
            - gotrip: idle -> trip
            - goshop: idel -> shop
            - goconverse: idel -> conve
            - pause: idle -> paused
            - gousercontrol: idle -> controled
        - trip:
            - arrived: trip -> idle
            - routefailed: trip -> idle (导航失败)
            - pause: idle -> paused
            - gousercontrol: idle -> controled
        - shop:
            - shopdone: shop -> idle
            - pause: idle -> paused
            - gousercontrol: idle -> controled
        - conve:
            - convedone: conve -> idle
            - pause: idle -> paused
            - gousercontrol: idle -> controled
        - paused:
            - active*: paused -> *
        - controled:
            - controlback: controled -> idle
    - Note: 目前不支持状态扩展
    """
    states = ['idle', 'trip', 'shop', 'conve', 'paused', 'controled']

    def __init__(self, config=None):
        self.pre_state = None
        # TODO: 后续添加扩展接口
        # Initialize the state machine
        self.machine = Machine(model=self, states=StateTransformer.states, initial='idle')

        # idle
        self.machine.add_transition(trigger='gotrip', source='idle', dest='trip')
        self.machine.add_transition(trigger='goshop', source='idle', dest='shop')
        self.machine.add_transition(trigger='goconverse', source='idle', dest='conve')

        # trip
        self.machine.add_transition(trigger='arrived', source='trip', dest='idle')
        self.machine.add_transition(trigger='routefailed', source='trip', dest='idle')

        # shop
        self.machine.add_transition(trigger='shopdone', source='shop', dest='idle')

        # conve
        self.machine.add_transition(trigger='convedone', source='conve', dest='idle')

        # pause
        self.machine.add_transition(trigger='pause', source='*', dest='paused', before='state_remember')

        # active
        self.machine.add_transition(trigger='active_trip', source='paused', dest='trip')
        self.machine.add_transition(trigger='active_idle', source='paused', dest='idle')
        self.machine.add_transition(trigger='active_shop', source='paused', dest='shop')
        self.machine.add_transition(trigger='active_conve', source='paused', dest='conve')

        # nothing
        self.machine.add_transition(trigger='nothing', source='*', dest='=')

        # controled
        self.machine.add_transition(trigger='gousercontrol', source='*', dest='controled')
        self.machine.add_transition(trigger='controlback', source='controled', dest='idle')

    def state_remember(self):
        if self.state != 'paused':  # 避免重复Pause
            self.pre_state = self.state

    def pause_back(self):
        if self.pre_state == 'trip':
            self.active_trip()
        elif self.pre_state == 'shop':
            self.active_shop()
        elif self.pre_state == 'conve':
            self.active_conve()
        elif self.pre_sate == 'idle':
            self.active_idle()