from typing import Any

PGSQL_DICT: dict[str, list[Any]] = {
    # Experiment
    "experiment": [
        """
    CREATE TABLE IF NOT EXISTS {table_name} (
        id UUID PRIMARY KEY,
        name TEXT,
        num_day INT4,
        status INT4, 
        cur_day INT4,
        cur_t FLOAT,
        config TEXT,
        error TEXT,
        created_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMPTZ NOT NULL DEFAULT CURRENT_TIMESTAMP
    )
""",
    ],
    # Agent Profile
    "agent_profile": [
        """
    CREATE TABLE IF NOT EXISTS {table_name} (
        id UUID PRIMARY KEY,
        name TEXT,
        profile JSONB
    )
""",
    ],
    # Agent Dialog
    "agent_dialog": [
        """
    CREATE TABLE IF NOT EXISTS {table_name} (
        id UUID,
        day INT4,
        t FLOAT,
        type INT4,
        speaker TEXT,
        content TEXT,
        created_at TIMESTAMPTZ
    )
""",
        "CREATE INDEX {table_name}_id_idx ON {table_name} (id)",
        "CREATE INDEX {table_name}_day_t_idx ON {table_name} (day,t)",
    ],
    # Agent Status
    "agent_status": [
        """
    CREATE TABLE IF NOT EXISTS {table_name} (
        id UUID,
        day INT4,
        t FLOAT,
        lng DOUBLE PRECISION,
        lat DOUBLE PRECISION,
        parent_id INT4,
        friend_ids UUID[],
        action TEXT,
        status JSONB,
        created_at TIMESTAMPTZ
    )
""",
        "CREATE INDEX {table_name}_id_idx ON {table_name} (id)",
        "CREATE INDEX {table_name}_day_t_idx ON {table_name} (day,t)",
    ],
    # Agent Survey
    "agent_survey": [
        """
    CREATE TABLE IF NOT EXISTS {table_name} (
        id UUID,
        day INT4,
        t FLOAT,
        survey_id UUID,
        result JSONB,
        created_at TIMESTAMPTZ
    )
""",
        "CREATE INDEX {table_name}_id_idx ON {table_name} (id)",
        "CREATE INDEX {table_name}_day_t_idx ON {table_name} (day,t)",
    ],
}
TO_UPDATE_EXP_INFO_KEYS_AND_TYPES: list[tuple[str, Any]] = [
    ("id", None),
    ("name", str),
    ("num_day", int),
    ("status", int),
    ("cur_day", int),
    ("cur_t", float),
    ("config", str),
    ("error", str),
    ("created_at", None),
    ("updated_at", None),
]
