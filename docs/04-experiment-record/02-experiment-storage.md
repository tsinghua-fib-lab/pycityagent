# Experiment Storage

In our framework, we provide two ways to record the details within an experiment.
- PostgreSQL
- Avro 

## PostgreSQL

### Usage

Provide `storage/pgsql` field in your yaml config file as follows.

```yaml
storage:
  pgsql:                   # PostgreSQL database settings
    enabled: true
    dsn: "postgresql://user:pass@host:port/dbname"

```
### Pg Table Definition

#### Experiment Meta Info
```sql
CREATE TABLE IF NOT EXISTS <table_name> (
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

```

#### Agent Profile
```sql
CREATE TABLE IF NOT EXISTS <table_name> (
    id UUID PRIMARY KEY,
    name TEXT,
    profile JSONB
)

```

#### Agent Dialog
```sql
CREATE TABLE IF NOT EXISTS <table_name> (
    id UUID,
    day INT4,
    t FLOAT,
    type INT4,
    speaker TEXT,
    content TEXT,
    created_at TIMESTAMPTZ
)
```

#### Agent Status
```sql
CREATE TABLE IF NOT EXISTS <table_name> (
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
CREATE INDEX <table_name>_id_idx ON <table_name> (id)
CREATE INDEX <table_name>_day_t_idx ON <table_name> (day,t)
```

#### Survey
```sql
CREATE TABLE IF NOT EXISTS <table_name> (
    id UUID,
    day INT4,
    t FLOAT,
    survey_id UUID,
    result JSONB,
    created_at TIMESTAMPTZ
)
CREATE INDEX <table_name>_id_idx ON <table_name> (id)
CREATE INDEX <table_name>_day_t_idx ON <table_name> (day,t)

```

## Avro

Provide `storage/avro` field in your yaml config file as follows.

```yaml
storage:
  avro:                   # Avro settings
    enabled: true
    path: "./avros"

```

### Usage

### Schema Definition

#### Experiment Meta Info
```json
{
    "type": "record",
    "name": "ExperimentInfo",
    "namespace": "pycityagent.simulation",
    "fields": [
        {"name": "id", "type": "string"},
        {"name": "name", "type": "string"},
        {"name": "num_day", "type": "int", "default": 0},
        {"name": "status", "type": "int"},
        {"name": "cur_day", "type": "int"},
        {"name": "cur_t", "type": "double"},
        {"name": "config", "type": "string"},
        {"name": "error", "type": "string"},
        {"name": "created_at", "type": "string"},
        {"name": "updated_at", "type": "string"},
    ],
}

```

#### Agent Profile
```json
 {
    "doc": "Agent属性",
    "name": "AgentProfile",
    "namespace": "com.socialcity",
    "type": "record",
    "fields": [
        {"name": "id", "type": "string"},
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

```

#### Agent Dialog
```json
{
    "doc": "Agent对话",
    "name": "AgentDialog",
    "namespace": "com.socialcity",
    "type": "record",
    "fields": [
        {"name": "id", "type": "string"},
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

```

#### Agent Status
```json
{
    "doc": "Agent状态",
    "name": "AgentStatus",
    "namespace": "com.socialcity",
    "type": "record",
    "fields": [
        {"name": "id", "type": "string"},
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
```

#### Institution Status
```json
{
    "doc": "Institution状态",
    "name": "InstitutionStatus",
    "namespace": "com.socialcity",
    "type": "record",
    "fields": [
        {"name": "id", "type": "string"},
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

```

#### Survey 
```json
{
    "doc": "Agent问卷",
    "name": "AgentSurvey",
    "namespace": "com.socialcity",
    "type": "record",
    "fields": [
        {"name": "id", "type": "string"},
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

```
