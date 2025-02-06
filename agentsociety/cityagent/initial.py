import random
import numpy as np
from agentsociety.cityagent import (BankAgent, FirmAgent, GovernmentAgent,
                                   NBSAgent, SocietyAgent)

import logging

logger = logging.getLogger("agentsociety")

async def initialize_social_network(simulation):
    """
    Initializes the social network between agents.

    - **Description**:
        - Creates friendship relationships between agents
        - Assigns relationship types (family, colleague, friend)
        - Sets relationship strengths based on type
        - Initializes chat histories and interaction records

    - **Returns**:
        - None
    """
    try:
        logger.info("Initializing social network...")

        # Define possible relationship types
        relation_types = ["family", "colleague", "friend"]

        # Get all agent IDs
        citizen_uuids = await simulation.filter(types=[SocietyAgent])
        for agent_id in citizen_uuids:
            # Randomly select 2-5 friends for each agent
            num_friends = random.randint(2, 5)
            possible_friends = [aid for aid in citizen_uuids if aid != agent_id]
            friends = random.sample(
                possible_friends, min(num_friends, len(possible_friends))
            )

            # Initialize friend relationships
            await simulation.update(agent_id, "friends", friends)

            # Initialize relationship types and strengths with each friend
            relationships = {}
            relation_type_map = {}

            for friend_id in friends:
                # Randomly select relationship type
                relation_type = random.choice(relation_types)
                # Set initial relationship strength range based on type
                if relation_type == "family":
                    strength = random.randint(60, 90)  # Higher strength for family
                elif relation_type == "colleague":
                    strength = random.randint(40, 70)  # Medium strength for colleagues
                else:  # friend
                    strength = random.randint(30, 80)  # Wide range for friends

                relationships[friend_id] = strength
                relation_type_map[friend_id] = relation_type

            # Update relationship strengths and types
            await simulation.update(agent_id, "relationships", relationships)
            await simulation.update(agent_id, "relation_types", relation_type_map)

            # Initialize empty chat histories and interaction records
            await simulation.update(
                agent_id, "chat_histories", {friend_id: "" for friend_id in friends}
            )
            await simulation.update(
                agent_id, "interactions", {friend_id: [] for friend_id in friends}
            )
        return True

    except Exception as e:
        print(f"Error initializing social network: {str(e)}")
        return False

def zipf_distribution(N, F, s=1.0):
    """
    Generates employee counts for F companies following Zipf's law, with total employees N.

    - **Description**:
        - Uses Zipf's law to distribute N total employees across F companies
        - The distribution follows a power law where employee count is proportional to 1/rank^s
        - Normalizes the distribution to ensure total employees equals N

    - **Parameters**:
        - `N`: Total number of employees across all companies
        - `F`: Number of companies to distribute employees across  
        - `s`: Power law exponent for Zipf's law, typically close to 1

    - **Returns**:
        - List of integer employee counts for each company, summing to N
    """
    # Calculate employee count for each rank (following Zipf's law distribution)
    ranks = np.arange(1, F + 1)  # Ranks from 1 to F
    sizes = 1 / (ranks ** s)  # Calculate employee count ratio according to Zipf's law

    # Calculate normalization coefficient to make total employees equal N
    total_size = np.sum(sizes)
    normalized_sizes = sizes / total_size * N  # Normalize to total employees N

    # Return employee count for each company (integers)
    return np.round(normalized_sizes).astype(int)

async def bind_agent_info(simulation):
    """
    Binds agent information including IDs for citizens, firms, government, banks and NBS.

    - **Description**:
        - Gathers all agent IDs and maps them between UUID and agent ID
        - Assigns employees to firms following Zipf's law distribution
        - Links citizens to government and bank systems

    - **Returns**:
        - None
    """
    logger.info("Binding economy relationship...")
    infos = await simulation.gather("id")
    citizen_uuids = await simulation.filter(types=[SocietyAgent])
    firm_uuids = await simulation.filter(types=[FirmAgent])
    government_uuids = await simulation.filter(types=[GovernmentAgent])
    bank_uuids = await simulation.filter(types=[BankAgent])
    nbs_uuids = await simulation.filter(types=[NBSAgent])
    citizen_agent_ids = []
    uid2agent, agent2uid = dict(), dict()
    for info in infos:
        for k, v in info.items():
            if k in citizen_uuids:
                citizen_agent_ids.append(v)
            uid2agent[k] = v
            agent2uid[v] = k
    citizen_agent_ids_cp = citizen_agent_ids.copy()
    random.shuffle(citizen_agent_ids_cp)
    employee_sizes = zipf_distribution(len(citizen_agent_ids_cp), len(firm_uuids))
    for firm_uuid, size in zip(firm_uuids, employee_sizes):
        await simulation.economy_update(uid2agent[firm_uuid], "employees", citizen_agent_ids_cp[:size])
        for citizen_agent_id in citizen_agent_ids_cp[:size]:
            await simulation.update(agent2uid[citizen_agent_id], "firm_id", uid2agent[firm_uuid])
        citizen_agent_ids_cp = citizen_agent_ids_cp[size:]
    for government_uuid in government_uuids:
        await simulation.economy_update(uid2agent[government_uuid], "citizens", citizen_agent_ids)
    for bank_uuid in bank_uuids:
        await simulation.economy_update(uid2agent[bank_uuid], "citizens", citizen_agent_ids)
    for nbs_uuid in nbs_uuids:
        await simulation.update(nbs_uuid, "citizens", citizen_uuids)
        await simulation.economy_update(uid2agent[nbs_uuid], "citizens", citizen_agent_ids)
    logger.info("Agent info binding completed!")
