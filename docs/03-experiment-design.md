# Design your Experiment

This guide covers the various tools available for intervention and observation within our framework.

## Survey and Interview

### Survey System

The simulation provides a comprehensive survey system for gathering structured feedback from agents:

```python
# Example of creating and sending a survey
import asyncio

from agentsociety import AgentSimulation
from agentsociety.configs import SimConfig
from agentsociety.survey import SurveyManager


async def main():
    # customize your config here
    sim_config = SimConfig()
    simulation = AgentSimulation(config=sim_config)
    survey_manager = SurveyManager()
    survey = survey_manager.create_survey(
        title="Job Satisfaction Survey",
        description="Understanding agent job satisfaction",
        pages=[
            {
                "name": "page1",
                "elements": [
                    {
                        "name": "satisfaction",
                        "title": "How satisfied are you with your job?",
                        "type": "rating",
                        "min_rating": 1,
                        "max_rating": 5,
                    }
                ],
            }
        ],
    )
    # Send survey to specific agents
    await simulation.send_survey(survey, agent_uuids=["agent1", "agent2"])


if __name__ == "__main__":
    asyncio.run(main())
```

### Interview System 

The interview system allows direct interaction with agents through messages.

```python
# Example of conducting an interview
import asyncio

from agentsociety import AgentSimulation
from agentsociety.configs import SimConfig


async def main():
    # customize your config here
    sim_config = SimConfig()
    simulation = AgentSimulation(config=sim_config)
    # Send interview to specific agents
    await simulation.send_interview_message(
        content="What are your career goals?",
        agent_uuids=['agent1']
    )


if __name__ == "__main__":
    asyncio.run(main())
```

Key features:
- Direct one-on-one interaction with agents
- Free-form responses
- Real-time conversation capabilities
- Support for both individual and group interviews

## Metrics Collection

### MLflow Integration

The `MlflowClient` class manages experiment tracking and metrics logging for agent simulations using [MLflow](https://mlflow.org/).

#### Metrics Logging

##### Directly use `MlflowClient` 

We provide property `mlflow_client` for `AgentSimulation` and `Agent` class.

```python
# Metric logging
await simulation.mlflow_client.log_metric(
    key="average_income",    # Metric name
    value=100.5,            # Metric value
    step=1                  # Time step 
)

# Batch logging of metrics
await simulation.mlflow_client.log_batch(
    metrics=[
        Metric(key="gdp", value=1000.0, step=1),
        Metric(key="population", value=500, step=1)
    ]
)
```

##### Use the Tool `ExportMlflowMetrics` 

```python
from agentsociety.tools import ExportMlflowMetrics


class CustomAgent(Agent):
    export_metric = ExportMlflowMetrics()

    async def forward(self):
        await self.export_metric({"key": 0}, clear_cache=True)  # Use the tool
```

## Message Interception

The message interception system provides control over Agent communications.

### Message Control System

To activate the message control system, simply use `ExpConfig.SetMessageIntercept`, e.g. `ExpConfig().SetMessageIntercept(mode="point", max_violation_time=3)`.

### `MessageBlock`

`MessageBlock` checks if the message is from/to any blacklisted entities.

#### `EdgeMessageBlock` Class

An implementation of `MessageBlockBase` designed to filter messages based on emotional provocativeness and manage a blacklist of sender-receiver pairs.

Any messages intercepted will be popped to the queue of `MessageBlockListener`.

- When a message is deemed invalid (emotionally provocative), and the sender has exceeded the maximum allowed violations (`max_violation_time`), this block adds the exact sender-receiver pair (from_uuid, to_uuid) to the blacklist.

#### `PointMessageBlock` Class
Similar to `EdgeMessageBlock`, also an implementation of `MessageBlockBase`.

Any messages intercepted will be popped to the queue of `MessageBlockListener`.

- It checks if messages are emotionally provocative and evaluates whether the sender has exceeded the violation limit, this block adds the exact sender-receiver pair (from_uuid, None) to the blacklist. (from_uuid, None) in a blacklist means the sender can no longer send out any messages.

### `MessageBlockListener` Class

A listener class that processes values from the blocked message queue asynchronously.

Get value from the queue every `get_queue_period` seconds continually.

## Examples

Here we provide examples on how to perform typical social experiments with our framework.

### 1.

PLACE-HOLDER

### 2.

PLACE-HOLDER

### 3.

PLACE-HOLDER

### 4.

PLACE-HOLDER
