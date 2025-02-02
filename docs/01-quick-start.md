# Quick Start

This guide helps you quickly set up a social simulation scenario with our framework.

---

## Run Example Simulation

We give a simple example to run a social simulation with 50 citizens in Beijing City using predefined agent templates and provided Beijing City data.

### LLM API Acquisition
To use this framework, you **need access to LLM APIs**. We support multiple providers:

- [DeepSeek](https://deepseek.com/)
- [OpenAI](https://openai.com/)
- [Qwen](https://tongyi.aliyun.com/)
- [SiliconFlow](https://siliconflow.cn/)
- [ZhipuAI](https://chatglm.cn/)

---

#### ZhipuAI (As Example)
1. Visit https://open.bigmodel.cn/
2. Register an account and authorize yourself at https://open.bigmodel.cn/usercenter/settings/auth/
3. Create an API key of `GLM-4-Flash` (free model) at https://open.bigmodel.cn/usercenter/apikeys/

### Configuration

#### 1. File-based Configuration

```python
from pycityagent.configs import (ExpConfig, SimConfig, WorkflowStep,
                                 load_config_from_file)
from pycityagent.simulation import AgentSimulation

sim_config = load_config_from_file("examples/example_sim_config.yaml", SimConfig)
exp_config = load_config_from_file("examples/example_exp_config.yaml", ExpConfig)


async def main():
    simulation = AgentSimulation.run_from_config(
        config=exp_config,
        sim_config=sim_config,
    )
    await simulation


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
```
##### `example_sim_config.yaml`
```yaml
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
    server: "mqtt.example.com"
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
##### `example_exp_config.yaml`
```yaml
agent_config:
    number_of_citizen: 50  # Number of citizens
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

#### 2. Fluent API Configuration

```python
from pycityagent.configs import (ExpConfig, SimConfig, WorkflowStep,
                                 load_config_from_file)
from pycityagent.simulation import AgentSimulation

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
        number_of_citizen=50,
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


async def main():
    simulation = AgentSimulation.run_from_config(
        config=exp_config,
        sim_config=sim_config,
    )
    await simulation


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())

```

## Simulation Observation

We'll give a brief introduction to the simulation observation methods.

To design your own experiment with interaction and intervene methods provided, please refer to [Experiment Design Guide](03-experiment-design).

### Visualization with Web Interface

We provide `pycityagent-ui` as our visualization tool within the python package.

You can either visualize a running simulation process in real-time or replay one completed simulation.

To activate the ui interface, you simply need to code these in your terminal. 
```bash
pycityagent-ui --pg-dsn=postgres://postgres:postgres@localhost:5432/socialcity?sslmode=disable --mqtt-broker=tcp://localhost:1883 --mqtt-username=username --mqtt-password=password --addr=localhost:8080 --mlflow-url=http://localhost:5000
```

- `--addr`: Address for the UI service (default: `localhost:8080`).
- `--mqtt-broker`: MQTT broker address (e.g., `"mqtt.example.com:1883`).
- `--mqtt-username`: Username for MQTT.
- `--mqtt-password`: Password for MQTT.
- `--pg-dsn`: PostgreSQL DSN for database connection.
- `--mlflow-url`: URL for MLflow server (e.g., `http://localhost:59000`).

```{admonition} Caution
:class: caution
To use this interface, you MUST deploy PostgreSQL, MLflow and MQTT first.
```
#### UI Home Page

The home page shown in the listening address lists all the simulation recorded in your deployed PostgreSQL DSN. 

![home-page](img/01-ui-home-page.jpg) 

There are several function buttons on the top left.

- `Experiment`: Display all conducted experiments. Click to jump to the detailed interaction page.
- `Survey`: Create and manage surveys to Agents within the simulation.
- `MLflow`: Direct you to the deployed MLflow web page.

#### Experiment Interaction

Click `Goto` shown in [UI Home Page](#ui-home-page) to interact with specific experiment.

In the experiment page, you can see the geographic position of each Agent.

- Mobility Trajectories.
- Chat messages among Agents.
- Economy activities.

![exp-page](img/01-exp-page.jpg)

Click one Agent avatar for detailed information.

- Interview specific Agents.
- Send surveys to Agents and collect their answers.
- Chat with Agents.

![exp-status](img/01-exp-status.jpg)


### Storage Experiment locally

Please check [Record Experiment with Avro](04-advanced-usage.md#record-experiment-with-avro) for details.

### Extract Specific Metrics

Please check [Metrics Collection](03-experiment-design.md#metrics-collection) for details.

## Customize Your Own Simulation

### Agent Configuration

Customize your citizens and institutions for simulation.

#### # of Agents
Configure the number of citizen agents using `ExpConfig.SetAgentConfig`.

```python
from pycityagent.configs import (ExpConfig, SimConfig, WorkflowStep,
                                 load_config_from_file)

exp_config = (
    ExpConfig(exp_name="test")
    .SetAgentConfig(
        number_of_citizen=50,    # Specify number of citizen agents
        number_of_firm=5,        # Number of firms
        number_of_bank=2,        # Number of banks 
        number_of_government=1,  # Number of government entities
        number_of_nbs=3          # Number of neighborhood services
        enable_institution=True  # Enable/disable institutional agents
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

#### Custom Agent Logics

To implement custom agent behaviors and logic, refer to the [Custom Agents Guide](02-custom-agents.md#customizing-the-agent-logic).

### City Environment Configuration

#### Simulation Configuration

##### Change to Other Cities

We use `Map` as the simulation environment.

To use a different city map:
1. Follow the map building guide at [MOSS Documentation](https://python-moss.readthedocs.io/en/latest/02-quick-start/index.html)
2. Configure the map in your simulation:

```python
from pycityagent.configs import (ExpConfig, SimConfig, WorkflowStep,
                                 load_config_from_file)
sim_config = SimConfig(
    .SetMapRequest(file_path="path/to_your_city_map.pb")
)
```

##### Simulation Time Configuration

```python
from pycityagent.configs import (ExpConfig, SimConfig, WorkflowStep,
                                 load_config_from_file)
sim_config = (
    SimConfig()
    .SetSimulatorRequest(
        task_name="citysim",           # Simulation task name
        start_step=8 * 3600,           # Start time (8:00 AM)
        total_step=24 * 3600,          # Simulation Steps for One day
        max_day=2,                     # Run for 2 days
        min_step_time=1               # Minimum time (seconds) between steps
    ) 
)
```

#### Global Environment Configuration

Set environment parameters with `ExpConfig.SetEnvironment`.

```python
from pycityagent.configs import (ExpConfig, SimConfig, WorkflowStep,
                                 load_config_from_file)

exp_config = (
    ExpConfig(exp_name="environment_test")
    .SetEnvironment(
        weather="The weather is normal",
        crime="The crime rate is low",
        pollution="The pollution level is low",
        temperature="The temperature is normal",
        day="Workday",
    )
)
```

## Next Steps

For advanced usage of our framework, explore the following topics:

### Data Export and Analysis
- **Avro Data Export**
  ```python
  # Enable Avro storage in simulation config
  sim_config = SimConfig(
      avro_config={
          "enabled": True,
          "path": "/path/to/avro/storage"
      }
  )
  ```

- **PostgreSQL Integration** 
  ```python
  # Enable PostgreSQL storage for frontend data
  sim_config = (
    SimConfig()    
    .SetPostgreSql(path="postgresql://user:pass@localhost:5432/db", enabled=True)
  )
  ```

### Customizing Agent Groups
```python
exp_config = (
    ExpConfig(exp_name="test")
    .SetAgentConfig(
        group_size=10,  # Set group size
        memory_config_func={
            SocietyAgent: custom_memory_config,
            FirmAgent: custom_firm_config
        },
    )
)
```

### Distributed Simulation

Setup Ray for distributed simulation

### Advanced Usage Guidance

For detailed implementation of these features, refer to:
- [Record Experiment with Avro](04-advanced-usage.md#record-experiment-with-avro)
- [Record Experiment with PostgreSQL](04-advanced-usage.md#record-experiment-with-postgresql)
- [Distributed Simulation Setup](04-advanced-usage.md#distributed-simulation)
