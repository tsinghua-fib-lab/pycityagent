# Advanced Usage

This guide provides advanced usage for our framework.

## Record Experiment with PostgreSQL

### Usage

Assign SimConfig with `SimConfig.SetPostgreSql`, e.g. `SimConfig().SetPostgreSql(path="postgresql://user:pass@localhost:5432/db", enabled=True)`.

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

## Record Experiment with Avro

### Usage

Assign SimConfig with `SimConfig.SetAvro`, e.g. `SimConfig().SetAvro(path="cache/avro", enabled=True)`.

### Schema Definition

#### Experiment Meta Info
```json
{
    "type": "record",
    "name": "ExperimentInfo",
    "namespace": "agentsociety.simulation",
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

## Distributed Simulation

Here is a simple example to run simulation in the same LAN.

```python
import asyncio
import logging

import ray

from agentsociety import AgentSimulation
from agentsociety.cityagent import (BankAgent, FirmAgent, GovernmentAgent,
                                   NBSAgent, SocietyAgent)
from agentsociety.cityagent.initial import (bind_agent_info,
                                           initialize_social_network)
from agentsociety.configs import SimConfig
from agentsociety.simulation import AgentSimulation

sim_config = (
    SimConfig()
    .SetLLMRequest(request_type="zhipuai", api_key="", model="GLM-4-Flash")
    .SetSimulatorRequest(min_step_time=1, primary_node_ip="<YOUR-PRIMARY-IP>")
    .SetMQTT(server="mqtt.example.com", username="user", port=1883, password="pass")
    .SetMapRequest(file_path="./ignore/map.pb")
    .SetMetricRequest(
        username="mlflow_user", password="mlflow_pass", mlflow_uri="http://mlflow:5000"
    )
)


async def run_simulation():
    simulation = AgentSimulation(
        config=sim_config,
        exp_name="system_log",
        logging_level=logging.INFO,
    )
    await simulation.init_agents(
        agent_count={
            SocietyAgent: 50,
            FirmAgent: 1,
            GovernmentAgent: 1,
            BankAgent: 1,
            NBSAgent: 1,
        },
    )
    await bind_agent_info(simulation)
    await initialize_social_network(simulation)


async def run_experiments():
    ray.init(address="auto")
    await run_simulation()


if __name__ == "__main__":
    asyncio.run(run_experiments())

```

```{admonition} Caution
:class: caution
- `SetMQTT`: `server` should be accessible for all nodes.
- `SetMetricRequest`: `mlflow_uri` should be accessible for all nodes. 
- `SetSimulatorRequest`: `primary_node_ip` should be accessible for all nodes. 
- `SetMapRequest`: the `file_path` is for the primary node.
```

### AgentGroup Configuration

In our framework, agents are grouped into several `AgentGroup`s, and each `AgentGroup` works as a `Ray` actor.

#### `ExpConfig.AgentConfig`

- `group_size`: controls the agent num for each `AgentGroup`, directly affect the computing pressure for a `Ray` actor.
