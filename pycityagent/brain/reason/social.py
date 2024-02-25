import json

async def handleConve(wk, retrives):
    """
    对话处理
    Conversation handler

    Args:
    - wk (WorkingMemory)
    - retrives (dict): the MemoryRetrive output collection

    Returns:
    - (Tuple([list[int], list[str]])): (id, message)
    """
    soul = wk._agent.Soul
    familiers = retrives['familiers']
    ids = []
    messages = []
    if wk.enable_social:
        # * 接受其他agent发送过来的消息
        if wk.msg_agent_unhandle:
            for from_id, content_dialog in wk.msg_agent_unhandle.items():
                if from_id in wk.agent_converse_buffer.keys():
                    # * 正在进行对话
                    if content_dialog[0]['content'] == 'End':
                        # * 接受到End, 说明对方认为对话已结束
                        if from_id in wk.msg_agent_still.keys():
                            del wk.msg_agent_still[from_id]
                    else:
                        # * 正常进行对话
                        wk.agent_converse_buffer[from_id] += content_dialog
                        dialog = wk.agent_converse_buffer[from_id]
                        print(dialog)
                        resp = soul.text_request(dialog)
                        if resp == 'Finished':
                            del wk.msg_agent_still[from_id]
                            ids.append(from_id)
                            messages.append('End')
                        else:
                            wk.agent_converse_buffer[from_id].append({
                                'role': 'assistant',
                                'content': resp
                            })
                            ids.append(from_id)
                            messages.append(resp)
                            print(f'回复: {resp}')
                            wk.msg_agent_still[from_id] = 20
                else:
                    # * 之前没有进行过对话 - 他人主动问好
                    # * 判断是否进行对话 - 目前只支持熟人对话
                    if from_id in familiers.keys():
                        wk.agent_converse_buffer[from_id].append({
                            'role': 'system',
                            'content': f'''和你对话的人是: {familiers[from_id]['name']}, 和你的关系是{familiers[from_id]['relation']} {familiers[from_id]['learned']}'''
                        })
                        wk.agent_converse_buffer[from_id] += content_dialog
                        dialog = wk.agent_converse_buffer[from_id]
                        resp = soul.text_request(dialog)
                        if resp == 'Finished':
                            # * 不理睬
                            ids.append(from_id)
                            messages.append('End')
                        else:
                            # * 回复
                            wk.agent_converse_buffer[from_id].append({
                                'role': 'assistant',
                                'content': resp
                            })
                            ids.append(from_id)
                            messages.append(resp)
                            wk.msg_agent_still[from_id] = 20
            wk.msg_agent_unhandle.clear()  # 清空
        else:
            # * 主动问好
            # * 判断周围是否有熟人
            familier_around = []
            for person in wk.sence['persons']:
                if person['id'] in familiers.keys():
                    familier_around.append((person, familiers[person['id']]))
            if len(familier_around) > 0:
                # 周围有熟人
                # * 感兴趣人物筛选
                dialog = wk.most_interest_dialog+[{'role': 'user', 'content': f'''我的基本信息为: {wk._agent.Image.get_profile()}'''}]
                familier_text = ''''''
                for person in familier_around:
                    familier_text += f'''[人物id: {person[0]['id']}, 姓名: {person[1]['name']}, 和我的关系: {person[1]['relation']}, 其他信息: {person[1]['learned']}]\n'''
                dialog += [{'role': 'user', 'content': f'''周围人物信息: \n{familier_text}'''}]
                resp = soul.text_request(dialog)
                try:
                    resp_dict = json.loads(resp)
                    interested_id = familiers[resp_dict['id']]
                    conve = resp_dict['conve']
                    # * 是否发起对话
                    if conve == '是':
                        # 发起对话
                        wk.agent_converse_buffer[interested_id].append({
                            'role': 'system',
                            'content': f'''和你对话的人是: {familiers[interested_id]['name']}, 和你的关系是{familiers[interested_id]['relation']} {familiers[interested_id]['learned']}'''
                        })
                        hello_dialog = wk.agent_converse_buffer[interested_id] + [{'role': 'user', 'content': f'''假设你主动向对方问好, 你会说什么?'''}]
                        hello = soul.text_request(hello_dialog)
                        wk.agent_converse_buffer[interested_id].append({'role': 'system', 'content': f'你主动问好说: {hello}'})
                        ids.append(interested_id)
                        messages.append(hello)
                        wk.msg_agent_still[interested_id] = 20
                except:
                    print("社交信息理解失败")

        # * 处理对话对象挂断或突然终止对话的情况
        to_del = []
        for id in wk.msg_agent_still.keys():
            wk.msg_agent_still[id] -= 1
            if wk.msg_agent_still[id] <= 0:
                to_del.append(id)
        for id in to_del:
            del wk.msg_agent_still[id]

    return (ids, messages)

async def startConve(wk):
    """
    判断是否进入/保持对话状态
    Whether enter or stay in 'conve' state

    Args:
    - wk (WorkingMemory)

    Returns:
    - (bool): if True, enter 'conve' state, else not
    """
    if len(wk.msg_agent_still) > 0:
        return True
    return False

async def endConve(wk):
    """
    判断是否结束对话(所有对话)
    Whther end conversations (all conversations)

    Args:
    - wk (WorkingMemory)

    Returns:
    - (bool): if True, all conversations are ended, else not
    """
    if len(wk.msg_agent_still) > 0:
        return False
    return True