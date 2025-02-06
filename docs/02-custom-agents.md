# Customize Agents

This document provides a detailed guide on how to customize the behavior logic of agents in our simulation environment. The behavior of agents is controlled by the `forward` method, which is triggered in a step-by-step manner, synchronized with the simulation environment's second-by-second update logic.

## Core Components of an Agent

An agent in our simulation environment is composed of several core components:

### Memory

There two types of `Memory` in our framework, `StreamMemory` and `StatusMemory`.

#### `StreamMemory`

`StreamMemory` is used to manage and store time-ordered memory information in a stream-like structure.

##### Main Components

- `collections.deque` for memory storage
- **Memory Tags** (`MemoryTag`):
   - Mobility: Movement-related memories
   - Social: Social interaction memories
   - Economy: Economic activities
   - Cognition: Cognitive processes
   - Event: Event-related memories
   - Other: Miscellaneous memories
 - **Memory Node** (`MemoryNode`):
   - tag: Memory category (MemoryTag)
   - day: Event day
   - t: Timestamp
   - location: Event location
   - description: Memory content
   - cognition_id: Optional reference to cognitive memory
   - id: Optional unique identifier

#### `StatusMemory`

`StatusMemory` is designed to unify three different types of memory (status, configuration, dynamic) into a single objective memory.

##### Main Components

- **Memory Types**:
   - `ProfileMemory`: Stores self-profile for the agent.
   - `StateMemory`: Stores status data of the agent.
   - `DynamicMemory`: Stores user-dynamically configured data.

#### Embedding Model
Embedding Model is used in the memory to:
- Convert text descriptions into vector representations
- Enable semantic search across memory entries
- Support similarity-based memory retrieval

To change the embedding model within the `Memory`, you simply need to assign it with `ExpConfig.SetAgentConfig`.

```python
from agentsociety.configs import (ExpConfig, SimConfig, WorkflowStep,
                                 load_config_from_file)
from agentsociety.llm import SimpleEmbedding

exp_config = ExpConfig(exp_name="test",).SetAgentConfig(
    embedding_model=SimpleEmbedding()
)
```
The incoming `embedding` is an instance of a subclass from `langchain_core.embeddings.Embeddings` and needs to implement `embed_query`, `embed_documents`.

#### Retrieve Specific Memory

##### Time-based Memory Retrieval
- `search_today`

##### ID-based Retrieval
- `get_by_ids`

##### Filter-based Memory Retrieval
- `search`
  - Semantic
  - Time Range
  - Memory Tag
  - Day Range
  - Top-K

### Urban Simulator
The Simulator serves as a bridge between agents and the physical entities in the simulation environment.
It manages bi-directional communication, allowing agents to perceive their surroundings and interact with the environment through actions.

#### Interact Methods

##### Environment Management
- `environment`
- `set_environment`
- `sence`
- `update_environment`

##### Map Item Query
- `map`
- `get_poi_cate`
- `get_poi_categories`

##### Logging History
- `get_log_list`
- `clear_log_list`

##### Time-related Operations
- `get_time`
- `get_simulator_day`
- `get_simulator_second_from_start_of_day`

##### Simulation Control
- `pause`
- `resume`

##### Person Information Retrieval
- `get_person`

### Economy Simulator
The Economy Client serves as a centralized economic settlement system that manages monetary flows between company entities and citizen entities in the simulation environment.

It handles transactions, resource allocation, and financial interactions within the virtual economy.

#### Interact Methods

##### Value Operations
- `get`: Get value of specific key
- `update`: Update value of specific key
- `add_delta_value`: Incremental update number type value

##### Currency Calculation
- `calculate_taxes_due`: Pay tax to the government
- `calculate_consumption`: Buy items from firms
- `calculate_real_gdp`: Calculate GDP
- `calculate_interest`: Calculate interest for bank accounts

##### Entity Information Retrieval
- `get_agent`
- `get_org`

##### Simulation Control
- `save`
- `load`

##### Logging History
- `get_log_list`
- `clear_log_list`

### LLM Client

The LLM Client manages communications between agents and large language models, representing the agent's "soul".

#### Core Functions

##### Communication Interface
- `atext_request`: Asynchronous chat completion

##### API Control
- `show_consumption`: Monitor token consumption
- `set_semaphore`

##### Request Configuration
- `set_temperature`: Adjust response randomness
- `set_max_tokens`: Control response length
- `set_top_p`: Configure sampling parameters
- `set_presence_penalty`: Adjust repetition avoidance

##### Logging History
- `get_log_list`
- `clear_log_list`

## Customizing the Agent logic

To customize the behavior of an agent, you can modify the `forward` method. 
This method is where the agent's logic is defined and executed in each simulation step. 
Here are two ways to customize the `forward` methods.

### Direct Implementation

A simple example is as follows.

```python
import asyncio

from agentsociety import Agent, AgentType


class CustomAgent(Agent):
    def __init__(self, name: str, **kwargs):
        super().__init__(name=name, type=AgentType.Citizen, **kwargs)

    async def forward(
        self,
    ):
        print(f"type:{self._type}")


async def main():
    agent = CustomAgent("custom_agent")
    await agent.forward()


if __name__ == "__main__":
    asyncio.run(main())
```


### Block Based Implementation

For complex behaviors, use `Block` to organize logic.

```python
import asyncio
from typing import Optional

from agentsociety import Simulator
from agentsociety.agent import Agent
from agentsociety.llm import LLM
from agentsociety.memory import Memory
from agentsociety.workflow import Block


class SecondCustomBlock(Block):

    def __init__(
        self,
        agent: Agent,
        llm: LLM,
        memory: Memory,
        simulator: Simulator,
    ):
        super().__init__(
            name="SecondCustomBlock", llm=llm, memory=memory, simulator=simulator
        )
        self._agent = agent

    async def forward(self):
        return f"SecondCustomBlock forward!"


class FirstCustomBlock(Block):
    second_block: SecondCustomBlock

    def __init__(
        self,
        agent: Agent,
        llm: LLM,
        memory: Memory,
        simulator: Simulator,
    ):
        super().__init__(
            name="FirstCustomBlock", llm=llm, memory=memory, simulator=simulator
        )
        self._agent = agent
        self.second_block = SecondCustomBlock(agent, llm, memory, simulator)

    async def forward(self):
        first_log = f"FirstCustomBlock forward!"
        second_log = await self.second_block.forward()
        if self._agent.enable_print:
            print(first_log, second_log)


class CustomAgent(Agent):

    configurable_fields = [
        "enable_print",
    ]
    default_values = {
        "enable_print": True,
    }
    fields_description = {
        "enable_print": "Enable Print Message",
    }
    first_block: FirstCustomBlock

    def __init__(
        self,
        name: str,
        llm_client: Optional[LLM] = None,
        simulator: Optional[Simulator] = None,
        memory: Optional[Memory] = None,
    ) -> None:
        super().__init__(
            name=name,
            llm_client=llm_client,
            simulator=simulator,
            memory=memory,
        )
        self.enable_print = True
        self.first_block = FirstCustomBlock(self, llm_client, memory, simulator)

    # Main workflow
    async def forward(self):
        await self.first_block.forward()


async def main():
    agent = CustomAgent(name="CustomAgent")
    print(agent.export_class_config())
    await agent.forward()


if __name__ == "__main__":
    asyncio.run(main())

```


### Using Tools
Tools provide reusable functionality that can be automatically bound to `Agent` or `Block`.

```python
from agentsociety.tools import Tool


class CustomTool(Tool):
    async def __call__(
        self,
    ):
        # Tool bound to agent
        agent = self.agent
        await agent.status.update("key", "value")
        # # Tool bound to block
        # block = self.block
        # await block.memory.status.update("key", "value")


class CustomAgent(Agent):
    my_tool = CustomTool()  # Tool automatically binds to agent instance

    async def forward(self):
        await self.my_tool()  # Use the tool

```
