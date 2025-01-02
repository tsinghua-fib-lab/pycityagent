PROFILE_SCHEMA = {
    "doc": "Agent属性",
    "name": "AgentProfile",
    "namespace": "com.socialcity",
    "type": "record",
    "fields": [
        {"name": "id", "type": "string"},  # uuid as string
        {"name": "name", "type": "string"},
        {"name": "gender", "type": "string"},
        {"name": "age", "type": "float"},
        {"name": "education", "type": "string"},
        {"name": "skill", "type": "string"},
        {"name": "occupation", "type": "string"},
        {"name": "family_consumption", "type": "string"},
        {"name": "consumption", "type": "string"},
        {"name": "personality", "type": "string"},
        {"name": "income", "type": "string"},
        {"name": "currency", "type": "float"},
        {"name": "residence", "type": "string"},
        {"name": "race", "type": "string"},
        {"name": "religion", "type": "string"},
        {"name": "marital_status", "type": "string"},
    ],
}

DIALOG_SCHEMA = {
    "doc": "Agent对话",
    "name": "AgentDialog",
    "namespace": "com.socialcity",
    "type": "record",
    "fields": [
        {"name": "id", "type": "string"},  # uuid as string
        {"name": "day", "type": "int"},
        {"name": "t", "type": "float"},
        {"name": "type", "type": "int"},
        {"name": "speaker", "type": "string"},
        {"name": "content", "type": "string"},
        {
            "name": "created_at",
            "type": {"type": "long", "logicalType": "timestamp-millis"},
        },
    ],
}

STATUS_SCHEMA = {
    "doc": "Agent状态",
    "name": "AgentStatus",
    "namespace": "com.socialcity",
    "type": "record",
    "fields": [
        {"name": "id", "type": "string"},  # uuid as string
        {"name": "day", "type": "int"},
        {"name": "t", "type": "float"},
        {"name": "lng", "type": "double"},
        {"name": "lat", "type": "double"},
        {"name": "parent_id", "type": "int"},
        {"name": "action", "type": "string"},
        {"name": "hungry", "type": "float"},
        {"name": "tired", "type": "float"},
        {"name": "safe", "type": "float"},
        {"name": "social", "type": "float"},
        {
            "name": "created_at",
            "type": {"type": "long", "logicalType": "timestamp-millis"},
        },
    ],
}

INSTITUTION_STATUS_SCHEMA = {
    "doc": "Institution状态",
    "name": "InstitutionStatus",
    "namespace": "com.socialcity",
    "type": "record",
    "fields": [
        {"name": "id", "type": "string"},  # uuid as string
        {"name": "day", "type": "int"},
        {"name": "t", "type": "float"},
        {"name": "type", "type": "int"},
        {"name": "nominal_gdp", "type": {"type": "array", "items": ["float", "int", "string", "null"]}},
        {"name": "real_gdp", "type": {"type": "array", "items": ["float", "int", "string", "null"]}},
        {"name": "unemployment", "type": {"type": "array", "items": ["float", "int", "string", "null"]}},
        {"name": "wages", "type": {"type": "array", "items": ["float", "int", "string", "null"]}},
        {"name": "prices", "type": {"type": "array", "items": ["float", "int", "string", "null"]}},
        {"name": "inventory", "type": ["int", "null"]},
        {"name": "price", "type": ["float", "null"]},
        {"name": "interest_rate", "type": ["float", "null"]},
        {"name": "bracket_cutoffs", "type": {"type": "array", "items": ["float", "int", "string", "null"]}},
        {"name": "bracket_rates", "type": {"type": "array", "items": ["float", "int", "string", "null"]}},
        {"name": "employees", "type": {"type": "array", "items": ["float", "int", "string", "null"]}},
    ],
}

SURVEY_SCHEMA = {
    "doc": "Agent问卷",
    "name": "AgentSurvey",
    "namespace": "com.socialcity",
    "type": "record",
    "fields": [
        {"name": "id", "type": "string"},  # uuid as string
        {"name": "day", "type": "int"},
        {"name": "t", "type": "float"},
        {"name": "survey_id", "type": "string"},
        {"name": "result", "type": "string"},
        {
            "name": "created_at",
            "type": {"type": "long", "logicalType": "timestamp-millis"},
        },
    ],
}
