from typing import Callable, Any
from pycityagent.ac.action import ActionType
from ..action import Action
from pycitysim.apphub import AgentMessage
import time

def encap_msg(msg, role='user', **kwargs):
    dialog = {'role': role, 'content': msg}
    dialog.update(kwargs)
    return dialog

class ShopAction(Action):
    '''Shop行为控制器'''
    def __init__(self, agent, sources: list[str] = None, before: Callable[[list], Any] = None) -> None:
        super().__init__(agent, ActionType.Comp, sources, before)

    async def Forward(self):
        # * 与模拟器对接 - 暂时没有
        # * 与AppHub对接
        profile = self._agent.Image.get_profile()
        self.consumption(profile)

    def consumption(self, profile, mall_info):
        dialogs = []
        system_prompt = f'''
                            你是一个在北京工作和生活的人。 
                            {profile} 
                            现在是2024年1月。
                            你需要为下一周的基本生活购买必需品。
                        '''
        dialogs.append(encap_msg(system_prompt, 'system'))
        actions_format = ['''{{'商品': 购买的商品的列表,'购买量': 每个商品的购买量，一个列表, '解释': '这种购买方式的原因'}}''']
        actions_candidates = ['''【食品】
                                米：10元/公斤
                                面粉：7.5元/公斤
                                新鲜蔬菜（如菠菜）：7元/500克
                                水果（如苹果）：15元/公斤
                                猪肉：30元/公斤
                                鸡肉：20元/公斤
                                鸡蛋：1.5元/个
                                牛奶：10元/升''',
                                '''【清洁用品】
                                    洗衣液：30元/瓶
                                    洗洁精：20元/瓶
                                    垃圾袋：0.3元/个''',
                                '''【个人护理用品】
                                    牙膏：10元/支
                                    洗发水：30元/瓶
                                    沐浴露：35元/瓶
                                    面巾纸：5元/包''',
                                '''【其他】
                                    矿泉水：1.7元/瓶
                                    面包：8元/个
                                    辣条：3元/包''']

        user_prompt = f'''
                        首先确定你的消费预算。以如下格式回答，不要有冗余的文本！
                        {{'消费预算': 一个代表购买必需品需要消耗的钱的数量的数字}}
                        '''
        dialogs.append(encap_msg(user_prompt))
        # * 对接一：确定消费预算
        self._agent.Hub.Update([AgentMessage(self._agent.Hub._agent_id, int(time.time()*1000), '我正在确定消费预算......', None, None)])
        msg = self._agent._soul.text_request(dialogs)
        self._agent.Hub.Update([AgentMessage(self._agent.Hub._agent_id, int(time.time()*1000), f'我的消费预算是: {msg}'), None, None])

        dialogs.append(encap_msg(msg, 'assistant'))

        # * 对接二：购物选择
        for cand in actions_candidates:
            user_prompt = f'''
                            购物中心里有
                            {cand}
                            你要买哪些商品，以如下格式回答，不要有冗余的文本！
                            {actions_format[0]}
                        '''
            self._agent.Hub.Update([AgentMessage(self._agent.Hub._agent_id, int(time.time()*1000), f'我看到了\n {cand}', None, None)])
            dialogs.append(encap_msg(user_prompt))
            msg = self._agent._soul.text_request(dialogs)
            self._agent.Hub.Update([AgentMessage(self._agent.Hub._agent_id, int(time.time()*1000), f'我的购买选择是: {msg}', None, None)])
            dialogs.append(encap_msg(msg, 'assistant'))
        
        self._agent.Hub.Update([AgentMessage(self._agent.Hub._agent_id, int(time.time()*1000), '购物完成', None, None)])