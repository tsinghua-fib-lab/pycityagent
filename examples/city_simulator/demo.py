import asyncio
import logging

from mosstool.map._map_util.const import AOI_START_ID
from pycityproto.city.person.v2 import person_pb2 as person_pb2

from pycityagent.agent import CitizenAgent
from pycityagent.environment.simulator import Simulator
from pycityagent.llm import LLM
from pycityagent.memory.memory import Memory
from pycityagent.workflow.tool import ResetAgentPosition, UpdateWithSimulator

logging.basicConfig(
    level=logging.INFO,
)


class SimDemoAgent(CitizenAgent):
    update_with_sim = UpdateWithSimulator()
    reset_pos = ResetAgentPosition()

    def __init__(
        self,
        name: str,
        llm_client: LLM | None = None,
        simulator: Simulator | None = None,
        memory: Memory | None = None,
    ) -> None:
        super().__init__(name, llm_client, simulator, memory)

    async def forward(self):
        # update memory with simulator
        await self.update_with_sim()
        MOTION_KEYS = {
            "status",
            "position",
            "v",
        }
        res_dict = {}
        for _key in MOTION_KEYS:
            try:
                res_dict[_key] = await self.memory.get(_key)
            except:
                pass
        agent_id = await self.memory.get("id")
        print(f"Status of Agent {agent_id}:{res_dict}")

    async def set_schedules(
        self,
    ):
        agent_id = await self.memory.get("id")
        await self.simulator.SetAoiSchedules(
            person_id=agent_id,
            target_positions=AOI_START_ID + 2,
        )


async def main():
    # SERVER_ADDRESS = "localhost:51102"
    # reading from config is also available
    simulator = Simulator(
        {
            "simulator": {
                # "server": SERVER_ADDRESS,
            },
            "map_request": {
                "mongo_uri": "******",
                "mongo_db": "srt",
                "mongo_coll": "map_beijing_extend_20241201",
                "cache_dir": "./ignore",
            },
        }
    )
    demo_agents = []
    memory = Memory(
        base={
            # 如果提供id则会绑定到模拟器中指定id的person，否则将在模拟器中新建一个person并返回id
            # "id":1,
            "home": {"aoi_position": {"aoi_id": AOI_START_ID + 1}},
        },
    )
    print("id", await memory.get("id"))
    print("home", await memory.get("home"))
    demo_agent = SimDemoAgent(
        name=f"Agent",
        simulator=simulator,
        memory=memory,
    )
    try:
        await demo_agent.reset_pos(aoi_id=AOI_START_ID + 1)
    except:
        pass
    demo_agents.append(demo_agent)
    for step in range(50):
        print(f"Step {step}")
        if step == 1:
            tasks = [demo_agent.set_schedules() for demo_agent in demo_agents]
            await asyncio.gather(*tasks)
            agent_id = await memory.get("id")
            print(await simulator.GetPerson(agent_id))
        else:
            tasks = [demo_agent.forward() for demo_agent in demo_agents]
            await asyncio.gather(*tasks)
        await asyncio.sleep(5)


if __name__ == "__main__":
    asyncio.run(main())
