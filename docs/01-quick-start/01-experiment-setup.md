# Via Config
To reduce programming pressure, our framework provides built-in agents which can be easily called by simply writing a config.
## Example
The minimal example to perform an experiment with our framework is as follows.
```python
import logging
import asyncio
from pycityagent import AgentSimulation

logging.getLogger("pycityagent").setLevel(logging.INFO)

exp_config = {
    "simulation_config": "config_template.yaml",
    "agent_config": {
        "number_of_citizen": 30,
        "number_of_firm": 1,
        "number_of_government": 1,
        "number_of_bank": 1,
        "number_of_nbs": 1,
    },
    "logging_level": logging.INFO,
    "workflow": [
        {"type": "run", "day": 1},
    ],
    "exp_name": "allinone",
}

async def main():
    await AgentSimulation.run_from_config(exp_config)

if __name__ == "__main__":
    asyncio.run(main())
```
We provide an example of the simulation config file `config_template.yaml` in `examples/`.

## Basic Structure of Experiment Config Dict

In this part we'll give a brief introduction to the basic usage of the config dict. The detailed usage of the config is shown in [custom-config](02-custom-config).

### simulation_config (Required)

The value is the config file path used for setting up the simulation, which is "config_template.yaml" in our example.

### agent_config (Required)

This part of config controls the details for initializing the agents

#### number_of_citizen: int

The number of citizen agents in the simulation. 
A Citizen Agent represents an individual in the real world, performing actions such as moving, making purchases, and engaging in social activities. It interacts with institution agents, like firms and banks.

#### number_of_firm: int

The number of firm agents in the simulation.
A Firm Agent represents a company in the real world, serving as the workplace for a Citizen Agent, also engaging in purchasing activities with the Citizen Agent.

#### number_of_government: int

The number of government agents in the simulation.
A Government Agent represents the government in the real world, responsible for taxing Citizen Agents and using the tax revenue to provide services to them.

#### number_of_bank: int

The number of bank agents in the simulation.
A Bank Agent represents a bank in the real world where a Citizen Agent can deposit money, and the bank provides interest on those deposits.

#### number_of_nbs: int

The number of NBS (National Bureau of Statistics) agents in the simulation.
A NBS Agent is similar to the real-world National Bureau of Statistics, responsible for collecting and analyzing macroeconomic metrics of economic activities.

### workflow (Required)
 
This part of config consists of a list of dict, which define the sequential actions in the simulation.
Following is the configurable fields for each dict.
#### type: str

A string indicating the type of step, which can be one of `"step"`, `"run"`, `"interview"`, `"survey"`, `"intervene"`, `"pause"`, or `"resume"`.

#### days: int if type is "run", else None

An integer specifying the duration in days when the `type` is `"run"`. Otherwise, it is `None`.

#### times: int if type is "step", else None

An integer specifying the number of times the step should be executed when the `type` is `"step"`. Otherwise, it is `None`.
