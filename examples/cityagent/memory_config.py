from mosstool.map._map_util.const import AOI_START_ID
from regex import B
from sympy import Dict


def get_memory_config():
    EXTRA_ATTRIBUTES = {
        # 需求信息
        "needs": (
            dict,
            {
                "hungry": 1,  # 饥饿感
                "tired": 1,  # 疲劳感
                "safe": 0.1,  # 安全需
                "social": 0.1,  # 社会需求
            },
            True,
        ),
        "current_need": (str, "none", True),
        "current_plan": (list, [], True),
        "current_step": (dict, {"intention": "", "type": ""}, True),
        "execution_context": (dict, {}, True),
        "plan_history": (list, [], True),
        # 位置信息
        "nowPlace": (dict, {"aoi_position": {"aoi_id": AOI_START_ID + 1}}, True),
    }

    PROFILE = {
        "gender": "male",
        "education": "Doctor",
        "consumption": "sightly low",
        "occupation": "Student",
        "age": 25,
        "skill": "Good at problem-solving",
        "family_consumption": "low",
        "personality": "outgoint",
        "income": "1500 元/月",
        "residence": "",
        "race": "Chinese",
        "religion": "none",
        "marital_status": "not married",
    }

    BASE = {
        "home": {"aoi_position": {"aoi_id": AOI_START_ID + 10000}},
        "work": {"aoi_position": {"aoi_id": AOI_START_ID + 20000}},
    }

    return EXTRA_ATTRIBUTES, PROFILE, BASE
