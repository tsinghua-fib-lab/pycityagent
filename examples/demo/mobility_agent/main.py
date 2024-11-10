import asyncio

import yaml

from pycityagent import CitizenAgent, Simulator
from pycityagent.llm import LLM, LLMConfig
from pycityagent.memory import Memory
from pycityagent.workflow import (Context, GetMap, NormalWorkflow, ReasonBlock,
                                  SencePOI)

from mobility_prompt import *
from utils import *


async def main():
    print("-----Loading configs...")
    with open("config_template.yaml", "r") as file:
        config = yaml.safe_load(file)

    # Step:1 prepare LLM client
    print("-----Loading LLM client...")
    llmConfig = LLMConfig(config["llm_request"])
    llm = LLM(llmConfig)

    # Step:2 prepare Simulator
    print("-----Loading Simulator...")
    simulator = Simulator(config["simulator_request"])

    # Step:3 prepare Memory
    print("-----Setting Memory...")
    (home, work) = choiceHW()
    Homeplace = (home[0], home[1])
    Workplace = (work[0], work[1])
    EXTRA_ATTRIBUTES = {
        "day": (str, "Monday"),
        "time": (str, "08:00"),
        "intentionTotal": (int, 6),
        "trajectory": (list, []),
        "home_": (tuple, Homeplace),
        "work_": (tuple, Workplace),
        "nowPlace": (tuple, Homeplace),
        "intention": str,
    }
    memory = Memory(
        config=EXTRA_ATTRIBUTES,
        profile={
            "gender": "male",
            "education": "Doctor",
            "consumption": "sightly low",
            "occupation": "Student",
        },
    )
    # Step:4 prepare Workflow
    print("-----Preparing Workflow...")
    workflow = NormalWorkflow(interval=5)
    intention_generation = ReasonBlock(
        context=Context(
            input_keys=[
                "gender",
                "education",
                "consumption",
                "occupation",
                "day",
                "time",
            ],
            update_keys=["intention"],
        ),
        title="intention_generation",
        description="generate mobility intention",
        format_template=INTENTION_GENERATION,
    )

    place_selection = ReasonBlock(
        context=Context(
            input_keys=["intention", "time", "nowPlace", {"map": GetMap()}],
            update_keys=["nowPlace", "time"],
        ),
        title="place_selection",
        description="select a place",
        self_define_function=get_place,
    )

    intention_generation.add_next_block(place_selection)
    workflow.set_start_block(intention_generation)

    # Step:5 preate Agent
    print("-----Preparing Agent...")
    agent = CitizenAgent("mobility_agent", llm, simulator, memory)
    agent.add_workflow(workflow)

    # Step:6 start the agent
    print("-----Starting...")
    await workflow.start(round=5)


if __name__ == "__main__":
    asyncio.run(main())
