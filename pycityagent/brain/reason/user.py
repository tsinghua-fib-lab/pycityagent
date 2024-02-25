from pycitysim.apphub import AgentMessage
import time
import json
import copy

async def hasUserControl(wk) -> bool:
    """
    判断是否有用户指令
    Whether there have user commond

    Args:
    - wk (WorkingMemory)

    Returns:
    - (bool): if True, have user commond, else not
    """
    soul = wk._agent.Soul
    hub = wk._agent.Hub
    if len(wk.msg_user_unhandle) > 0:
        # * 理解用户对话目的
        understand_dialog = copy.deepcopy(wk.understanding_prompt)
        user_dialog = []
        contin_flag = True
        for user_message in wk.msg_user_unhandle:
            content = user_message.content
            sub = [{'role': 'user', 'content': content}]
            user_dialog += sub
            print(f'[用户消息]: {content}')
            if '开' in content or '启' in content or 'enable' in content :
                if '用户交互' in content or 'interaction' in content:
                    wk._agent.enable_user_interaction()
                    hub.Update([AgentMessage(hub._agent_id, int(time.time()*1000), '已启动用户交互功能', None, None)])
                    contin_flag = False
                elif wk.enable_user_interaction and ('街景' in content or 'streetview' in content):
                    wk._agent.enable_streetview()
                    hub.Update([AgentMessage(hub._agent_id, int(time.time()*1000), '已启动街景功能(周围存在街景信息时自动呈现于屏幕右下角)', None, None)])
                    contin_flag = False
                elif wk.enable_user_interaction and ('经济' in content or 'economy' in content):
                    wk._agent.enable_economy_behavior()
                    hub.Update([AgentMessage(hub._agent_id, int(time.time()*1000), '已启动经济行为模拟', None, None)])
                    contin_flag = False
                elif wk.enable_user_interaction and ('社交' in content or 'social' in content):
                    wk._agent.enable_social_behavior()
                    hub.Update([AgentMessage(hub._agent_id, int(time.time()*1000), '已启动社交行为模拟', None, None)])
                    contin_flag = False
            elif '关' in content or 'diable' in content or '闭' in content:
                if '用户交互' in content or 'interaction' in content:
                    wk._agent.disable_user_interaction()
                    hub.Update([AgentMessage(hub._agent_id, int(time.time()*1000), '已关闭用户交互功能', None, None)])
                    contin_flag = False
                elif wk.enable_user_interaction and ('街景' in content or 'streetview' in content):
                    wk._agent.disable_streetview()
                    hub.Update([AgentMessage(hub._agent_id, int(time.time()*1000), '已关闭街景功能', None, None)])
                    contin_flag = False
                elif wk.enable_user_interaction and ('经济' in content or 'economy' in content):
                    wk._agent.disable_economy_behavior()
                    hub.Update([AgentMessage(hub._agent_id, int(time.time()*1000), '已关闭经济行为模拟', None, None)])
                    contin_flag = False
                elif wk.enable_user_interaction and ('社交' in content or 'social' in content):
                    wk._agent.disable_social_behavior()
                    hub.Update([AgentMessage(hub._agent_id, int(time.time()*1000), '已关闭社交行为模拟', None, None)])
                    contin_flag = False
                
        if not contin_flag:
            return False
        if not wk.enable_user_interaction:
            # * 关闭了交互功能
            hub.Update([AgentMessage(hub._agent_id, int(time.time()*1000), '抱歉, 我无法处理您的信息, 可能是因为您关闭了用户交互通道或该Agent不支持用户交互', None, None)])
            return False
        understand_dialog += user_dialog
        understand = soul.text_request(understand_dialog)

        if understand == '对话':
            wk.set_user_converse_background()
            dialog = copy.deepcopy(wk.user_converse_buffer)
            if wk.current_target != None:
                dialog.insert(3, {'role': 'system', 'content': f'你目前的计划: {wk.current_target}'})
            dialog += user_dialog
            print(dialog)
            resp = soul.text_request(dialog)
            if "Error" in resp:
                hub.Update([AgentMessage(hub._agent_id, int(time.time()*1000), "抱歉, 我暂时无法理解您的意思", None, None)])
            else:
                wk.user_converse_buffer += user_dialog
                wk.user_converse_buffer += [{'role': 'assistant', 'content': resp}]
                print(wk.user_converse_buffer)  # 添加到记忆中
                hub.Update([AgentMessage(hub._agent_id, int(time.time()*1000), resp, None, None)])
                wk.msg_user_unhandle = []
            return False
        elif understand == '控制':
            commond_to_target_dialog = [
                {'role': 'system', 'content': '你是一名语义理解大师, 你需要理解用户输入的目的, 并从第一视角[我]出发返回理解结果'},
                {'role': 'system', 'content': '例如用户输入: 你现在去买菜, 你将输出: 我现在要去买菜'},
                {'role': 'system', 'content': '例如用户输入: 你现在去公司工作, 你将输出: 我现在准备去公司工作'}
            ]
            for user_message in wk.msg_user_unhandle:
                content = user_message.content
                commond_to_target_dialog += [{'role': 'user', 'content': content}]
            wk.current_target = soul.text_request(commond_to_target_dialog)
            wk.has_user_command = True
            wk.msg_user_unhandle = []
            return True
        else:
            # * 无法理解
            hub.Update([AgentMessage(hub._agent_id, int(time.time()*1000), '抱歉，我无法理解您的话，您可以尝试换一种表达方式以帮助我理解', None, None)])
            wk.msg_user_unhandle = []
            return False

async def endUserControl(wk) -> bool:
    """
    判断用户控制是否已结束
    Whether user control has ended

    Args:
    - wk (WorkingMemory)

    Returns:
    - (bool): if True, ended, else not
    """
    if wk.has_user_command == False:
        return True
    return False