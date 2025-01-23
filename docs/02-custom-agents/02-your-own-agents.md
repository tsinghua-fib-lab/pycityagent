# Customize Your Own Agents

We develop our abstract `Agent` class for users to inherit and provide two ways to implement their own logic. 
- Directly implement the internal forward logic within the agent for simple, specific behaviors. 
- For more complex or reusable logic, we recommend utilizing the concept of `Blocks` to enhance modularity and abstraction.

## Direct Implementation

A simple example is as follows. 
```python
import asyncio

from pycityagent import Agent, AgentType


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


## Block Based Implementation
```python
import asyncio
from typing import Optional

from pycityagent import Simulator
from pycityagent.agent import Agent
from pycityagent.llm import LLM
from pycityagent.memory import Memory
from pycityagent.workflow import Block


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

Here we implement the agent forward logic with block `FirstCustomBlock`.
The logic within a block can also divide into more blocks, like `SecondCustomBlock` in our example. 
