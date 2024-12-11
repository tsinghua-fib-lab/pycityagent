def get_memory_config(Homeplace, Workplace):
    EXTRA_ATTRIBUTES = {
        # 需求信息
        "needs": (dict, {
            'hungry': 0.1,  # 饥饿感
            'tired': 0.1,   # 疲劳感
            'safe': 0.1,    # 安全需
            'social': 0.1,  # 社会需求
        }, True),
        "current_need": (str, "none", True),
        "current_plan": (list, [], True),
        "current_step": (dict, {"intention": "", "type": ""}, True),
        "plan_history": (list, [], True),
        
        # 位置信息
        "nowPlace": (tuple, Homeplace, True),
    }

    PROFILE = {
        "gender": "male",
        "education": "Doctor",
        "consumption": "sightly low",
        "occupation": "Student",
        "home": (tuple, Homeplace, True),
        "work": (tuple, Workplace, True),
    }

    return EXTRA_ATTRIBUTES, PROFILE