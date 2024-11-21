import asyncio

import numpy as np
import yaml

from examples.mobility_agent.utils import (choiceHW, event2poi_gravity,
                                           getDirectEventID)
from pycityagent import CitizenAgent, Simulator
from pycityagent.llm import LLM, LLMConfig
from pycityagent.memory import Memory
from pycityagent.workflow import FormatPrompt, GetMap, log_and_check


# time is a str, like "10:00", add a hour to time
def time_add(time):
    hour, minute = time.split(":")
    hour = int(hour) + 3
    return f"{hour}:{minute}"


INTENTION_GENERATION = """
        I'm a {gender}, my education level is {education}, my consumption level is {consumption} and my education level is {education}.
        Today is {day}, now is {time}.
        What my should do next?
        Please select from ['eat', 'have breakfast', 'have lunch', 'have dinner', 'do shopping', 'do sports', 'excursion', 'leisure or entertainment', 'medical treatment', 'handle the trivialities of life', 'banking and financial services', 'government and political services', 'cultural institutions and events']
        Your ouput only contains one of the above actions without any other words.
        """


# Define your own Agent
class MobilityAgent(CitizenAgent):
    # Rewrite forward function —— your main workflow
    get_map = GetMap()

    @log_and_check(record_function_calling=True)
    async def forward(self):
        # Control your workflow, you can do anything you want here
        # Prepare your prompt
        intention_generation = FormatPrompt(
            template=INTENTION_GENERATION,
        )
        totalIntention = await self.memory.get("intentionTotal")
        for i in range(totalIntention):
            # Step1: intention generation —— this is a LLM request
            # 1.1 format the prompt —— you can also format the prompt with other methods
            # Notice: If you don't want to use FormatPrompt, you can always desing your own work as long as you give the LLM request a dialog
            intention_generation.format(
                **{
                    key: await self.memory.get(key)
                    for key in intention_generation.variables
                }
            )
            # 1.2 Invoke LLM request
            intention = await self.LLM.atext_request(intention_generation.to_dialog())

            # Step2: POI selection —— gravity model
            nowPlace = await self.memory.get("nowPlace")
            time = await self.memory.get("time")
            map = await self.get_map()

            eventId = getDirectEventID(intention)
            POIs = event2poi_gravity(map, eventId, nowPlace)
            options = list(range(len(POIs)))
            probabilities = [item[2] for item in POIs]
            sample = np.random.choice(
                options, size=1, p=probabilities
            )  # 根据计算出来的概率值进行采样
            nextPlace = POIs[sample[0]]
            nextPlace = (nextPlace[0], nextPlace[1])
            time = time_add(time)

            await self.memory.update("nowPlace", nextPlace)
            await self.memory.update("time", time)
            print(f"intention: {intention}, time: {time}, nextPlace: {nextPlace}")


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

    # Step:4 prepare Agent
    mobility_agent = MobilityAgent(
        name="MobilityAgent", llm_client=llm, simulator=simulator, memory=memory
    )

    await mobility_agent.forward()


if __name__ == "__main__":
    asyncio.run(main())
