import random

from pycityagent.cityagent import (BankAgent, FirmAgent, GovernmentAgent,
                                   NBSAgent, SocietyAgent)


async def initialize_social_network(simulation):
    """
    初始化智能体之间的社交网络，包括好友关系类型、好友关系和社交关系强度
    """
    try:
        print("Initializing social network...")

        # 定义可能的关系类型
        relation_types = ["family", "colleague", "friend"]

        # 获取所有智能体ID
        agent_ids = simulation.agent_uuids
        for agent_id in agent_ids:
            # 为每个智能体随机选择2-5个好友
            num_friends = random.randint(2, 5)
            possible_friends = [aid for aid in agent_ids if aid != agent_id]
            friends = random.sample(
                possible_friends, min(num_friends, len(possible_friends))
            )

            # 初始化好友关系
            await simulation.update(agent_id, "friends", friends)

            # 初始化与每个好友的关系类型和关系强度
            relationships = {}
            relation_type_map = {}

            for friend_id in friends:
                # 随机选择关系类型
                relation_type = random.choice(relation_types)
                # 根据关系类型设置初始关系强度范围
                if relation_type == "family":
                    strength = random.randint(60, 90)  # 家人关系强度较高
                elif relation_type == "colleague":
                    strength = random.randint(40, 70)  # 同事关系强度中等
                else:  # friend
                    strength = random.randint(30, 80)  # 朋友关系强度范围较广

                relationships[friend_id] = strength
                relation_type_map[friend_id] = relation_type

            # 更新关系强度和类型
            await simulation.update(agent_id, "relationships", relationships)
            await simulation.update(agent_id, "relation_types", relation_type_map)

            # 初始化空的聊天历史和互动记录
            await simulation.update(
                agent_id, "chat_histories", {friend_id: [] for friend_id in friends}
            )
            await simulation.update(
                agent_id, "interactions", {friend_id: [] for friend_id in friends}
            )

        print("Social network initialization completed!")
        return True

    except Exception as e:
        print(f"Error initializing social network: {str(e)}")
        return False


async def bind_agent_info(simulation):
    """
    绑定智能体的信息，包括公民、公司、政府、银行和NBS的ID
    """
    print("Binding agent info...")
    infos = await simulation.gather("id")
    citizen_uuids = await simulation.filter(types=[SocietyAgent])
    firm_uuids = await simulation.filter(types=[FirmAgent])
    government_uuids = await simulation.filter(types=[GovernmentAgent])
    bank_uuids = await simulation.filter(types=[BankAgent])
    nbs_uuids = await simulation.filter(types=[NBSAgent])
    citizen_agent_ids = []
    firm_ids = []
    id2uuid = {}
    for info in infos:
        for k, v in info.items():
            if k in citizen_uuids:
                citizen_agent_ids.append(v)
            elif k in firm_uuids:
                firm_ids.append(v)
                id2uuid[v] = k
            elif k in government_uuids:
                government_id = v
            elif k in bank_uuids:
                bank_id = v
            elif k in nbs_uuids:
                nbs_id = v
    for citizen_uuid in citizen_uuids:
        random_firm_id = random.choice(firm_ids)
        await simulation.update(citizen_uuid, "firm_id", random_firm_id)
        await simulation.update(citizen_uuid, "government_id", government_id)
        await simulation.update(citizen_uuid, "bank_id", bank_id)
        await simulation.update(citizen_uuid, "nbs_id", nbs_id)
    for firm_uuid in firm_uuids:
        await simulation.update(firm_uuid, "employees", citizen_uuids)
        await simulation.update(firm_uuid, "employees_agent_id", citizen_agent_ids)
    for government_uuid in government_uuids:
        await simulation.update(government_uuid, "citizens", citizen_uuids)
        await simulation.update(government_uuid, "citizens_agent_id", citizen_agent_ids)
    for bank_uuid in bank_uuids:
        await simulation.update(bank_uuid, "citizens", citizen_uuids)
        await simulation.update(bank_uuid, "citizens_agent_id", citizen_agent_ids)
    for nbs_uuid in nbs_uuids:
        await simulation.update(nbs_uuid, "firm_id", random.choice(firm_ids))
    print("Agent info binding completed!")
