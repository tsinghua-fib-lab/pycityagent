import asyncio

import pycityproto.city.economy.v2.economy_pb2 as economyv2

from pycityagent.agent import Agent, AgentType
from pycityagent.economy.econ_client import EconomyClient
from pycityagent.environment.simulator import Simulator
from pycityagent.llm.llm import LLM
from pycityagent.memory.memory import Memory

SERVER_ADDRESS = "localhost:50051"


class EconDemoAgent(Agent):
    def __init__(
        self,
        name: str,
        type: AgentType = AgentType.Unspecified,
        llm_client: LLM | None = None,
        economy_client: EconomyClient | None = None,
        simulator: Simulator | None = None,
        memory: Memory | None = None,
    ) -> None:
        super().__init__(name, type, llm_client, economy_client, simulator, memory)

    async def forward(self):
        econ_client = self.economy_client
        _id = await self.memory.get("id")
        try:
            await econ_client.add_agents(
                {
                    "id": _id,
                    "currency": 100 + _id,
                }
            )
        except:
            pass
        print(f"Currency of agent {_id}:{await econ_client.get(_id,'currency')}")


class EconDemoBank(Agent):
    def __init__(
        self,
        name: str,
        type: AgentType = AgentType.Unspecified,
        llm_client: LLM | None = None,
        economy_client: EconomyClient | None = None,
        simulator: Simulator | None = None,
        memory: Memory | None = None,
    ) -> None:
        super().__init__(name, type, llm_client, economy_client, simulator, memory)

    async def forward(self):
        econ_client = self.economy_client
        _id = await self.memory.get("id")
        try:
            await econ_client.add_orgs(
                {
                    "id": _id,
                    "type": economyv2.ORG_TYPE_BANK,
                    "interest_rate": 0.1,
                    "currency": 0,
                }
            )
        except:
            pass
        await econ_client.calculate_interest(
            org_id=_id, agent_ids=[i for i in range(5)]
        )
        print(f"Currency of bank {_id}:{await econ_client.get(_id,'currency')}")


async def main():
    # check https://git.fiblab.net/llmsim/economysim to start server first
    econ_client = EconomyClient(server_address=SERVER_ADDRESS)
    econ_agents = []
    for ii in range(5):
        memory = Memory(
            base={
                "id": ii,
            },
        )
        econ_agent = EconDemoAgent(
            name=f"DemoAgent{ii}",
            memory=memory,
            economy_client=econ_client,
        )
        econ_agents.append(econ_agent)
    econ_bank = EconDemoBank(
        name=f"DemoBank",
        memory=Memory(
            base={
                "id": 500,
            },
        ),
        economy_client=econ_client,
    )
    for econ_agent in econ_agents:
        await econ_agent.forward()
    await econ_bank.forward()
    # after update
    print("After Update")
    for econ_agent in econ_agents:
        await econ_agent.forward()
    await econ_bank.forward()


if __name__ == "__main__":
    asyncio.run(main())
