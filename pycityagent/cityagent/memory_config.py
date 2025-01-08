import random
from collections import deque

import numpy as np
import pycityproto.city.economy.v2.economy_pb2 as economyv2
from mosstool.map._map_util.const import AOI_START_ID

pareto_param = 8
payment_max_skill_multiplier = 950
payment_max_skill_multiplier = float(payment_max_skill_multiplier)
pmsm = payment_max_skill_multiplier
pareto_samples = np.random.pareto(pareto_param, size=(1000, 10))
clipped_skills = np.minimum(pmsm, (pmsm - 1) * pareto_samples + 1)
sorted_clipped_skills = np.sort(clipped_skills, axis=1)
agent_skills = list(sorted_clipped_skills.mean(axis=0))


def memory_config_societyagent():
    EXTRA_ATTRIBUTES = {
        "city": "New York",
        # 需求信息
        "type": (str, "citizen"),
        "needs": (
            dict,
            {
                "hungry": random.random(),  # 饥饿感
                "tired": random.random(),  # 疲劳感
                "safe": random.random(),  # 安全需
                "social": random.random(),  # 社会需求
            },
            True,
        ),
        "current_need": (str, "none", True),
        "current_plan": (list, [], True),
        "current_step": (dict, {"intention": "", "type": ""}, True),
        "execution_context": (dict, {}, True),
        "plan_history": (list, [], True),
        # cognition
        "emotion": (
            dict,
            {
                "sadness": 5,
                "joy": 5,
                "fear": 5,
                "disgust": 5,
                "anger": 5,
                "surprise": 5,
            },
            True,
        ),
        "attitude": (dict, {}, True),
        "thought": (str, "Currently nothing good or bad is happening", True),
        "emotion_types": (str, "Relief", True),
        "incident": (list, [], True),
        "city": (str, "Texas", True),
        "work_skill": (
            float,
            random.choice(agent_skills),
            True,
        ),  # 工作技能, 即每小时的工资
        "tax_paid": (float, 0.0, True),  # 纳税
        "consumption_currency": (float, 0.0, True),  # 月消费
        "goods_demand": (int, 0, True),
        "goods_consumption": (int, 0, True),
        "work_propensity": (float, 0.0, True),
        "consumption_propensity": (float, 0.0, True),
        "income_currency": (float, 0.0, True),  # 月收入
        "to_income": (float, 0.0, True),
        "to_consumption_currency": (float, 0.0, True),
        "firm_id": (int, 0, True),
        "government_id": (int, 0, True),
        "bank_id": (int, 0, True),
        "nbs_id": (int, 0, True),
        "dialog_queue": (deque(maxlen=3), [], True),
        "firm_forward": (int, 0, True),
        "bank_forward": (int, 0, True),
        "nbs_forward": (int, 0, True),
        "government_forward": (int, 0, True),
        "forward": (int, 0, True),
        "depression": (float, 0.0, True),
        "ubi_opinion": (list, [], True),
        # social
        "friends": (list, [], True),  # 好友列表
        "relationships": (dict, {}, True),  # 与每个好友的关系强度
        "relation_types": (dict, {}, True),
        "chat_histories": (dict, {}, True),  # 所有聊天历史记录
        "interactions": (dict, {}, True),  # 所有互动记录
        "to_discuss": (dict, {}, True),
        # economy
        "working_experience": (list, [], True),
        "work_hour_month": (float, 160, True),
        "work_hour_finish": (float, 0, True),
        # mobility
        "environment": (str, "The environment outside is good", True),
    }

    PROFILE = {
        "name": random.choice(
            [
                "Alice",
                "Bob",
                "Charlie",
                "David",
                "Eve",
                "Frank",
                "Grace",
                "Helen",
                "Ivy",
                "Jack",
                "Kelly",
                "Lily",
                "Mike",
                "Nancy",
                "Oscar",
                "Peter",
                "Queen",
                "Rose",
                "Sam",
                "Tom",
                "Ulysses",
                "Vicky",
                "Will",
                "Xavier",
                "Yvonne",
                "Zack",
            ]
        ),
        "gender": random.choice(["male", "female"]),
        "age": random.randint(18, 65),
        "education": random.choice(
            ["Doctor", "Master", "Bachelor", "College", "High School"]
        ),
        "skill": random.choice(
            [
                "Good at problem-solving",
                "Good at communication",
                "Good at creativity",
                "Good at teamwork",
                "Other",
            ]
        ),
        "occupation": random.choice(
            [
                "Student",
                "Teacher",
                "Doctor",
                "Engineer",
                "Manager",
                "Businessman",
                "Artist",
                "Athlete",
                "Other",
            ]
        ),
        "family_consumption": random.choice(["low", "medium", "high"]),
        "consumption": random.choice(["sightly low", "low", "medium", "high"]),
        "personality": random.choice(
            ["outgoint", "introvert", "ambivert", "extrovert"]
        ),
        "income": "0",
        "currency": random.randint(1000, 100000),
        "residence": random.choice(["city", "suburb", "rural"]),
        "race": random.choice(
            [
                "Chinese",
                "American",
                "British",
                "French",
                "German",
                "Japanese",
                "Korean",
                "Russian",
                "Other",
            ]
        ),
        "religion": random.choice(
            ["none", "Christian", "Muslim", "Buddhist", "Hindu", "Other"]
        ),
        "marital_status": random.choice(
            ["not married", "married", "divorced", "widowed"]
        ),
    }

    BASE = {
        "home": {
            "aoi_position": {"aoi_id": AOI_START_ID + random.randint(1000, 10000)}
        },
        "work": {
            "aoi_position": {"aoi_id": AOI_START_ID + random.randint(1000, 10000)}
        },
    }

    return EXTRA_ATTRIBUTES, PROFILE, BASE


def memory_config_firm():
    EXTRA_ATTRIBUTES = {
        "type": (int, economyv2.ORG_TYPE_FIRM),
        "price": (float, float(np.mean(agent_skills))),
        "inventory": (int, 0),
        "employees": (list, []),
        "employees_agent_id": (list, []),
        "nominal_gdp": (list, []),  # useless
        "real_gdp": (list, []),
        "unemployment": (list, []),
        "wages": (list, []),
        "prices": (list, [float(np.mean(agent_skills))]),
        "working_hours": (list, []),
        "depression": (list, []),
        "consumption_currency": (list, []),
        "income_currency": (list, []),
        "locus_control": (list, []),
        "bracket_cutoffs": (
            list,
            list(np.array([0, 9875, 40125, 85525, 163300, 207350, 518400]) / 12),
        ),
        "bracket_rates": (list, [0.1, 0.12, 0.22, 0.24, 0.32, 0.35, 0.37]),
        "interest_rate": (float, 0.03),
        "citizens": (list, []),
        "citizens_agent_id": (list, []),
        "firm_id": (int, 0),
    }
    return EXTRA_ATTRIBUTES, {"currency": 1e12}, {}


def memory_config_government():
    EXTRA_ATTRIBUTES = {
        "type": (int, economyv2.ORG_TYPE_GOVERNMENT),
        # 'bracket_cutoffs': (list, list(np.array([0, 97, 394.75, 842, 1607.25, 2041, 5103])*100/12)),
        "bracket_cutoffs": (
            list,
            list(np.array([0, 9875, 40125, 85525, 163300, 207350, 518400]) / 12),
        ),
        "bracket_rates": (list, [0.1, 0.12, 0.22, 0.24, 0.32, 0.35, 0.37]),
        "citizens": (list, []),
        "citizens_agent_id": (list, []),
        "nominal_gdp": (list, []),  # useless
        "real_gdp": (list, []),
        "unemployment": (list, []),
        "wages": (list, []),
        "prices": (list, [float(np.mean(agent_skills))]),
        "working_hours": (list, []),
        "depression": (list, []),
        "consumption_currency": (list, []),
        "income_currency": (list, []),
        "locus_control": (list, []),
        "inventory": (int, 0),
        "interest_rate": (float, 0.03),
        "price": (float, float(np.mean(agent_skills))),
        "employees": (list, []),
        "employees_agent_id": (list, []),
        "firm_id": (int, 0),
    }
    return EXTRA_ATTRIBUTES, {"currency": 1e12}, {}


def memory_config_bank():
    EXTRA_ATTRIBUTES = {
        "type": (int, economyv2.ORG_TYPE_BANK),
        "interest_rate": (float, 0.03),
        "citizens": (list, []),
        "citizens_agent_id": (list, []),
        "bracket_cutoffs": (
            list,
            list(np.array([0, 9875, 40125, 85525, 163300, 207350, 518400]) / 12),
        ),  # useless
        "bracket_rates": (list, [0.1, 0.12, 0.22, 0.24, 0.32, 0.35, 0.37]),
        "inventory": (int, 0),
        "nominal_gdp": (list, []),  # useless
        "real_gdp": (list, []),
        "unemployment": (list, []),
        "wages": (list, []),
        "prices": (list, [float(np.mean(agent_skills))]),
        "working_hours": (list, []),
        "depression": (list, []),
        "consumption_currency": (list, []),
        "income_currency": (list, []),
        "locus_control": (list, []),
        "price": (float, float(np.mean(agent_skills))),
        "employees": (list, []),
        "employees_agent_id": (list, []),
        "firm_id": (int, 0),
    }
    return EXTRA_ATTRIBUTES, {"currency": 1e12}, {}


def memory_config_nbs():
    EXTRA_ATTRIBUTES = {
        "type": (int, economyv2.ORG_TYPE_NBS),
        "nominal_gdp": (list, []),
        "real_gdp": (list, []),
        "unemployment": (list, []),
        "wages": (list, []),
        "prices": (list, [float(np.mean(agent_skills))]),
        "working_hours": (list, []),
        "depression": (list, []),
        "consumption_currency": (list, []),
        "income_currency": (list, []),
        "locus_control": (list, []),
        "citizens": (list, []),
        "citizens_agent_id": (list, []),
        "firm_id": (int, 0),
        "bracket_cutoffs": (
            list,
            list(np.array([0, 9875, 40125, 85525, 163300, 207350, 518400]) / 12),
        ),  # useless
        "bracket_rates": (list, [0.1, 0.12, 0.22, 0.24, 0.32, 0.35, 0.37]),
        "inventory": (int, 0),
        "interest_rate": (float, 0.03),
        "price": (float, float(np.mean(agent_skills))),
        "employees": (list, []),
        "employees_agent_id": (list, []),
    }
    return EXTRA_ATTRIBUTES, {}, {}
