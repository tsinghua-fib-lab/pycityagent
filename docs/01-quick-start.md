# Quick Start

This guide helps you quickly set up a basic social simulation scenario using predefined agent templates.

---

## Configuration

### 1. File-based Configuration

```python
from pycityagent.configs import (ExpConfig, SimConfig, WorkflowStep,
                                 load_config_from_file)

sim_config = load_config_from_file("examples/example_sim_config.yaml", SimConfig)
exp_config = load_config_from_file("examples/example_exp_config.yaml", ExpConfig)
```
`example_sim_config.yaml`
- ```yaml
    llm_request:
        request_type: zhipuai
        api_key: ""
        model: GLM-4-Flash

    simulator_request:
        task_name: "citysim"              
        max_day: 1000                     
        start_step: 28800                 
        total_step: 31536000              
        log_dir: "./log"                  
        min_step_time: 1000               
        primary_node_ip: "localhost"      

    mqtt:
        server: sim1.fiblab.tech 
        port: 1883 
        username: "username"
        password: "password"

    map_request:
        file_path: "./ignore/map.pb"

    metric_request:
        mlflow: 
            username: "username"
            password: "password"
            mlflow_uri: "localhost:59000"

    pgsql:
        enabled: false     
        dsn: "postgresql://user:pass@localhost/db"         

    avro:
        enabled: false
        path: "./cache"          

    ```
`example_exp_config.yaml`
- ```yaml
    agent_config:
        number_of_citizen: 100  # Number of citizens
        enable_institution: false  # Whether institutions are enabled in the experiment

    workflow: [
        {"type": "run", "days": 1}
    ]

    environment:
        weather: "The weather is normal"
        crime: "The crime rate is low"
        pollution: "The pollution level is low"
        temperature: "The temperature is normal"
        day: "Workday"

    message_intercept:
        mode: "point"  # Mode can be 'point' or 'edge'
        max_violation_time: 3  # Maximum violation time


    exp_name: "my_experiment"  # Experiment name

    llm_semaphore: 200  # Semaphore value for LLM operations

    ```

### 2. Fluent API Configuration

```python
from pycityagent.configs import (ExpConfig, SimConfig, WorkflowStep,
                                 load_config_from_file)

sim_config = (
    SimConfig()
    .SetLLMRequest(request_type="zhipuai", api_key="", model="GLM-4-Flash")
    .SetSimulatorRequest(min_step_time=1)
    .SetMQTT(server="mqtt.example.com", username="user", port=1883, password="pass")
    .SetMapRequest(file_path="./ignore/map.pb")
    .SetMetricRequest(
        username="mlflow_user", password="mlflow_pass", mlflow_uri="http://mlflow:5000"
    )
    .SetPostgreSql(path="postgresql://user:pass@localhost:5432/db", enabled=True)
)
exp_config = (
    ExpConfig(exp_name="test", llm_semaphore=201)
    .SetAgentConfig(
        number_of_citizen=100,
        number_of_firm=0,
        number_of_government=0,
        number_of_bank=0,
        number_of_nbs=0,
        enable_institution=False,
    )
    .SetWorkFlow([WorkflowStep(type="run", days=1)])
    .SetEnvironment(
        weather="The weather is normal",
        crime="The crime rate is low",
        pollution="The pollution level is low",
        temperature="The temperature is normal",
        day="Workday",
    )
    .SetMessageIntercept(mode="point", max_violation_time=3)
)

```
