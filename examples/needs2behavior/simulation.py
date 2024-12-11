import asyncio
import yaml

from examples.needs2behavior.cityagent import MyAgent
from examples.needs2behavior.utils import choiceHW
from pycityagent.environment.simulator import Simulator
from pycityagent.llm.llm import LLM
from pycityagent.llm.llmconfig import LLMConfig
from pycityagent.memory.memory import Memory
from .memory_config import get_memory_config


async def main():
    print("-----Loading configs...")
    with open("__config_template.yaml", "r") as file:
        config = yaml.safe_load(file)

    # Step:1 prepare LLM client
    print("-----Loading LLM client...")
    llmConfig = LLMConfig(config["llm_request"])
    llm = LLM(llmConfig)

    # Step:2 prepare Simulator
    print("-----Loading Simulator...")
    SERVER_ADDRESS = "localhost:51102"
    simulator = Simulator(
        {
            "simulator": {
                "server": SERVER_ADDRESS,
            },
            "map_request": {
                "mongo_uri": "mongodb://sim:FiblabSim1001@mgo.db.fiblab.tech:8635",
                "mongo_db": "srt",
                "mongo_coll": "map_beijing_extend_20241201",
                "cache_dir": "../cache",
            },
        }
    )

    # Step:3 prepare Memory
    print("-----Setting Memory...")
    (home, work) = choiceHW()
    Homeplace = (home[0], home[1])
    Workplace = (work[0], work[1])
    EXTRA_ATTRIBUTES, PROFILE = get_memory_config(Homeplace, Workplace)
    memory = Memory(
        config=EXTRA_ATTRIBUTES,
        profile=PROFILE,
    )

    # Step:4 prepare Agent
    my_agent = MyAgent(
        name="MyAgent", llm_client=llm, simulator=simulator, memory=memory
    )

    # Step:5 run
    for i in range(10):
        await my_agent.forward()


if __name__ == "__main__":
    asyncio.run(main())