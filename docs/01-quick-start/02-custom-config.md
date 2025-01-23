# Custom Config

Here we'll show the detailed configuration for configs, thus supporting more customized experiments.

## Config Structure for `run_from_config`

### Required Fields

```python
config = {
    "simulation_config": str,          # Path to simulation YAML config
    "agent_config": {                  # Agent initialization parameters
        "number_of_citizen": int,      # Number of citizen agents (>=0)
        "number_of_firm": int,         # Number of firm agents (>=0)
        "number_of_government": int,   # Number of government agents (>=0)
        "number_of_bank": int,         # Number of bank agents (>=0)
        "number_of_nbs": int,         # Number of NBS agents (>=0)
    },
    "workflow": List[Dict],           # List of workflow steps
    "exp_name": str                   # Unique experiment identifier
}
```

### Optional Fields

```python
config = {
    "logging_level": int,             # Default: logging.INFO
    "random_seed": int,               # Default: None
    "save_dir": str,                  # Default: "./results"
    "checkpoint_dir": str,            # Default: "./checkpoints"
    "debug_mode": bool,               # Default: False
    "verbose": bool                   # Default: True
}
```

### Workflow Types

```python
workflows = [
    # Run simulation for specific days
    {"type": "run", "day": 5},
    
    # Execute single steps
    {"type": "step", "times": 10},
    
    # Interview agents
    {"type": "interview", "target": "citizen", "count": 5},
    
    # Conduct surveys
    {"type": "survey", "population": "all"},
    
    # Intervention actions
    {"type": "intervene", "action": "policy_change"},
    
    # Flow control
    {"type": "pause"},
    {"type": "resume"}
]
```

## Config Structure for simulation

```yaml
llm_request:       # LLM service configuration
simulator_request: # Simulation environment settings
metric_request:    # Metrics tracking configuration
storage:          # Data storage settings
```


### 1. LLM Request Configuration
```yaml
llm_request:
  text_request:
    request_type: "openai"    # Options: openai, azure, anthropic, etc.
    api_key: "sk-..."        # Your API key
    model: "gpt-4"          # Model identifier
  
  img_understand_request:    # Image understanding service
    request_type: "none"     # Set to none if not using
    api_key: "none"
    model: "none"
  
  img_generate_request:      # Image generation service
    request_type: "none"     # Set to none if not using
    api_key: "none"
    model: "none"
```

### 2. Simulator Request Configuration
```yaml
simulator_request:
  simulator:
    min_step_time: 1        # Minimum time step in simulation. Unit: s.
  
  mqtt:                     # MQTT connection settings
    server: "mqtt.example.com"
    username: "user"
    port: 1883
    password: "pass"
  
  map_request:             # Map data configuration
    mongo_uri: "mongodb://..."
    mongo_db: "srt"
    mongo_coll: "map_beijing_extend_20241201"
    cache_dir: "./ignore"
  
  streetview_request:      # Street view service settings
    engine: "baidumap"    # Options: baidumap, googlemap
    mapAK: "your-baidu-key"   # Required for Baidu Maps
    proxy: "proxy-address"    # Required for Google Maps
```

### 3. Metric Request Configuration
```yaml
metric_request:
  mlflow:                  # MLflow tracking configuration
    username: "mlflow_user"
    password: "mlflow_pass"
    mlflow_uri: "https://mlflow.example.com"
```

### 4. Storage Configuration

We provide two ways to record details in an experiment. Avro for local storage and PostgreSQL for database storage.

```yaml
storage:
  pgsql:                   # PostgreSQL database settings
    enabled: true
    dsn: "postgresql://user:pass@host:port/dbname"
  avro:                   # Avro settings
    enabled: true
    path: "./avros"

```
