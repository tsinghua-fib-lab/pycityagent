import json
import logging
import math
import random
from operator import itemgetter
from typing import List

import numpy as np
import ray

from agentsociety.environment.simulator import Simulator
from agentsociety.llm import LLM
from agentsociety.memory import Memory
from agentsociety.workflow.block import Block
from agentsociety.workflow.prompt import FormatPrompt
from .utils import clean_json_response
from .dispatcher import BlockDispatcher


logger = logging.getLogger("agentsociety")


PLACE_TYPE_SELECTION_PROMPT = """
As an intelligent decision system, please determine the type of place the user needs to visit based on their input requirement.
User Plan: {plan}
User requirement: {intention}
Your output must be a single selection from {poi_category} without any additional text or explanation.

Please response in json format (Do not return any other text), example:
{{
    "place_type": "shopping"
}}
"""

PLACE_SECOND_TYPE_SELECTION_PROMPT = """
As an intelligent decision system, please determine the type of place the user needs to visit based on their input requirement.
User Plan: {plan}
User requirement: {intention}
Your output must be a single selection from {poi_category} without any additional text or explanation.

Please response in json format (Do not return any other text), example:
{{
    "place_type": "shopping"
}}
"""

PLACE_ANALYSIS_PROMPT = """
As an intelligent analysis system, please determine the type of place the user needs to visit based on their input requirement.
User Plan: {plan}
User requirement: {intention}

Your output must be a single selection from ['home', 'workplace', 'other'] without any additional text or explanation.

Please response in json format (Do not return any other text), example:
{{
    "place_type": "home"
}}
"""

RADIUS_PROMPT = """As an intelligent decision system, please determine the maximum travel radius (in meters) based on the current emotional state.

Current weather: {weather}
Current temperature: {temperature}
Your current emotion: {emotion_types}
Your current thought: {thought}

Please analyze how these emotions would affect travel willingness and return only a single integer number between 3000-200000 representing the maximum travel radius in meters. A more positive emotional state generally leads to greater willingness to travel further.

Please response in json format (Do not return any other text), example:
{{
    "radius": 10000
}}
"""


def gravity_model(pois):
    pois_Dis = {
        "1k": [],
        "2k": [],
        "3k": [],
        "4k": [],
        "5k": [],
        "6k": [],
        "7k": [],
        "8k": [],
        "9k": [],
        "10k": [],
        "more": [],
    }
    for poi in pois:
        iflt10k = True
        for d in range(1, 11):
            if (d - 1) * 1000 <= poi[1] < d * 1000:
                pois_Dis["{}k".format(d)].append(poi)
                iflt10k = False
                break
        if iflt10k:
            pois_Dis["more"].append(poi)

    res = []
    distanceProb = []
    for poi in pois:
        iflt10k = True
        for d in range(1, 11):
            if (d - 1) * 1000 <= poi[1] < d * 1000:
                n = len(pois_Dis["{}k".format(d)])
                S = math.pi * ((d * 1000) ** 2 - ((d - 1) * 1000) ** 2)
                density = n / S
                distance = poi[1]
                distance = distance if distance > 1 else 1

                # distance decay coefficient, use the square of distance to calculate, so that distant places are less likely to be selected
                weight = density / (distance**2)  # the original weight is reasonable
                res.append((poi[0]["name"], poi[0]["id"], weight, distance))
                distanceProb.append(1 / (math.sqrt(distance)))
                iflt10k = False
                break

    distanceProb = np.array(distanceProb)
    distanceProb = distanceProb / np.sum(distanceProb)
    distanceProb = list(distanceProb)

    options = list(range(len(res)))
    sample = list(
        np.random.choice(options, size=50, p=distanceProb)
    )  # sample based on the probability value

    get_elements = itemgetter(*sample)
    random_elements = get_elements(res)

    # normalize the weight to become the true probability value
    weightSum = sum(item[2] for item in random_elements)
    final = [
        (item[0], item[1], item[2] / weightSum, item[3]) for item in random_elements
    ]
    return final


class PlaceSelectionBlock(Block):
    """
    Select destination
    PlaceSelectionBlock
    """

    configurable_fields: List[str] = ["search_limit"]
    default_values = {"search_limit": 50}

    def __init__(self, llm: LLM, memory: Memory, simulator: Simulator):
        super().__init__(
            "PlaceSelectionBlock", llm=llm, memory=memory, simulator=simulator
        )
        self.description = "Used to select and determine destinations for unknown locations (excluding home and workplace), such as choosing specific shopping malls, restaurants and other places"
        self.typeSelectionPrompt = FormatPrompt(PLACE_TYPE_SELECTION_PROMPT)
        self.secondTypeSelectionPrompt = FormatPrompt(
            PLACE_SECOND_TYPE_SELECTION_PROMPT
        )
        self.radiusPrompt = FormatPrompt(RADIUS_PROMPT)
        # configurable fields
        self.search_limit = 50

    async def forward(self, step, context):
        poi_cate = self.simulator.get_poi_cate()
        self.typeSelectionPrompt.format(
            plan=context["plan"],
            intention=step["intention"],
            poi_category=list(poi_cate.keys()),
        )
        levelOneType = await self.llm.atext_request(self.typeSelectionPrompt.to_dialog(), response_format={"type": "json_object"})  # type: ignore
        try:
            levelOneType = clean_json_response(levelOneType)
            levelOneType = json.loads(levelOneType)["place_type"]
            sub_category = poi_cate[levelOneType]
        except Exception as e:
            logger.warning(f"Level One Type Selection: wrong type of poi, raw response: {levelOneType}")
            levelOneType = random.choice(list(poi_cate.keys()))
            sub_category = poi_cate[levelOneType]
        self.secondTypeSelectionPrompt.format(
            plan=context["plan"], intention=step["intention"], poi_category=sub_category
        )
        levelTwoType = await self.llm.atext_request(self.secondTypeSelectionPrompt.to_dialog(), response_format={"type": "json_object"})  # type: ignore
        try:
            levelTwoType = clean_json_response(levelTwoType)
            levelTwoType = json.loads(levelTwoType)["place_type"]
        except Exception as e:
            logger.warning(f"Level Two Type Selection: wrong type of poi, raw response: {levelTwoType}")
            levelTwoType = random.choice(sub_category)
        center = await self.memory.status.get("position")
        center = (center["xy_position"]["x"], center["xy_position"]["y"])
        self.radiusPrompt.format(
            emotion_types=await self.memory.status.get("emotion_types"),
            thought=await self.memory.status.get("thought"),
            weather=self.simulator.sence("weather"),
            temperature=self.simulator.sence("temperature"),
        )
        radius = await self.llm.atext_request(self.radiusPrompt.to_dialog(), response_format={"type": "json_object"})  # type: ignore
        try:
            radius = int(json.loads(radius)["radius"])
            pois = ray.get(
                self.simulator.map.query_pois.remote(
                    center=center,
                    category_prefix=levelTwoType,
                    radius=radius,
                    limit=self.search_limit,
                )
            )
        except Exception as e:
            logger.warning(f"Error querying pois: {e}")
            radius = 10000
            pois = ray.get(
                self.simulator.map.query_pois.remote(
                    center=center,
                    category_prefix=levelTwoType,
                    radius=radius,
                    limit=self.search_limit,
                )
            )
        if len(pois) > 0:
            pois = gravity_model(pois)
            probabilities = [item[2] for item in pois]
            options = list(range(len(pois)))
            sample = np.random.choice(
                options, size=1, p=probabilities
            )  # sample based on the probability value
            nextPlace = pois[sample[0]]
            nextPlace = (nextPlace[0], nextPlace[1])
            # save the destination to context
            context["next_place"] = nextPlace
            node_id = await self.memory.stream.add_mobility(
                description=f"For {step['intention']}, I selected the destination: {nextPlace}"
            )
            return {
                "success": True,
                "evaluation": f"Successfully selected the destination: {nextPlace}",
                "consumed_time": 5,
                "node_id": node_id,
            }
        else:
            pois = ray.get(self.simulator.map.get_poi.remote())
            poi = random.choice(pois)
            nextPlace = (poi["name"], poi["aoi_id"])
            # save the destination to context
            context["next_place"] = nextPlace
            node_id = await self.memory.stream.add_mobility(
                description=f"For {step['intention']}, I selected the destination: {nextPlace}"
            )
            return {
                "success": True,
                "evaluation": f"Successfully selected the destination: {nextPlace}",
                "consumed_time": 5,
                "node_id": node_id,
            }


class MoveBlock(Block):
    """
    Execute mobility operations
    MoveBlock
    """

    def __init__(self, llm: LLM, memory: Memory, simulator: Simulator):
        super().__init__("MoveBlock", llm=llm, memory=memory, simulator=simulator)
        self.description = "Used to execute specific mobility operations, such as returning home, going to work, or visiting a specific location"
        self.placeAnalysisPrompt = FormatPrompt(PLACE_ANALYSIS_PROMPT)

    async def forward(self, step, context):
        agent_id = await self.memory.status.get("id")
        self.placeAnalysisPrompt.format(
            plan=context["plan"], intention=step["intention"]
        )
        response = await self.llm.atext_request(self.placeAnalysisPrompt.to_dialog(), response_format={"type": "json_object"})  # type: ignore
        try:
            response = clean_json_response(response)
            response = json.loads(response)["place_type"]
        except Exception as e:
            logger.warning(f"Place Analysis: wrong type of place, raw response: {response}")
            response = "home"
        if response == "home":
            home = await self.memory.status.get("home")
            home = home["aoi_position"]["aoi_id"]
            nowPlace = await self.memory.status.get("position")
            node_id = await self.memory.stream.add_mobility(
                description=f"I returned home"
            )
            if (
                "aoi_position" in nowPlace
                and nowPlace["aoi_position"]["aoi_id"] == home
            ):
                return {
                    "success": True,
                    "evaluation": f"Successfully returned home (already at home)",
                    "to_place": home,
                    "consumed_time": 0,
                    "node_id": node_id,
                }
            await self.simulator.set_aoi_schedules(
                person_id=agent_id,
                target_positions=home,
            )
            number_poi_visited = await self.memory.status.get("number_poi_visited")
            number_poi_visited += 1
            await self.memory.status.update("number_poi_visited", number_poi_visited)
            return {
                "success": True,
                "evaluation": f"Successfully returned home",
                "to_place": home,
                "consumed_time": 45,
                "node_id": node_id,
            }
        elif response == "workplace":
            # 返回到工作地点
            work = await self.memory.status.get("work")
            work = work["aoi_position"]["aoi_id"]
            nowPlace = await self.memory.status.get("position")
            node_id = await self.memory.stream.add_mobility(
                description=f"I went to my workplace"
            )
            if (
                "aoi_position" in nowPlace
                and nowPlace["aoi_position"]["aoi_id"] == work
            ):
                return {
                    "success": True,
                    "evaluation": f"Successfully reached the workplace (already at the workplace)",
                    "to_place": work,
                    "consumed_time": 0,
                    "node_id": node_id,
                }
            await self.simulator.set_aoi_schedules(
                person_id=agent_id,
                target_positions=work,
            )
            number_poi_visited = await self.memory.status.get("number_poi_visited")
            number_poi_visited += 1
            await self.memory.status.update("number_poi_visited", number_poi_visited)
            return {
                "success": True,
                "evaluation": f"Successfully reached the workplace",
                "to_place": work,
                "consumed_time": 45,
                "node_id": node_id,
            }
        else:
            # 移动到其他地点
            next_place = context.get("next_place", None)
            nowPlace = await self.memory.status.get("position")
            node_id = await self.memory.stream.add_mobility(
                description=f"I went to {next_place}"
            )
            if next_place != None:
                await self.simulator.set_aoi_schedules(
                    person_id=agent_id,
                    target_positions=next_place[1],
                )
            else:
                while True:
                    aois = ray.get(self.simulator.map.get_aoi.remote())
                    r_aoi = random.choice(aois)
                    if len(r_aoi["poi_ids"]) > 0:
                        r_poi = random.choice(r_aoi["poi_ids"])
                        break
                poi = ray.get(self.simulator.map.get_poi.remote(r_poi))
                next_place = (poi["name"], poi["aoi_id"])
                await self.simulator.set_aoi_schedules(
                    person_id=agent_id,
                    target_positions=next_place[1],
                )
            number_poi_visited = await self.memory.status.get("number_poi_visited")
            number_poi_visited += 1
            await self.memory.status.update("number_poi_visited", number_poi_visited)
            return {
                "success": True,
                "evaluation": f"Successfully reached the destination: {next_place}",
                "to_place": next_place[1],
                "consumed_time": 45,
                "node_id": node_id,
            }


class MobilityNoneBlock(Block):
    """
    空操作
    MobilityNoneBlock
    """

    def __init__(self, llm: LLM, memory: Memory):
        super().__init__("MobilityNoneBlock", llm=llm, memory=memory)
        self.description = "Used to handle other cases"

    async def forward(self, step, context):
        node_id = await self.memory.stream.add_mobility(
            description=f"I finished {step['intention']}"
        )
        return {
            "success": True,
            "evaluation": f'Finished executing {step["intention"]}',
            "consumed_time": 0,
            "node_id": node_id,
        }


class MobilityBlock(Block):
    place_selection_block: PlaceSelectionBlock
    move_block: MoveBlock
    mobility_none_block: MobilityNoneBlock

    def __init__(self, llm: LLM, memory: Memory, simulator: Simulator):
        super().__init__("MobilityBlock", llm=llm, memory=memory, simulator=simulator)
        # 初始化所有块
        self.place_selection_block = PlaceSelectionBlock(llm, memory, simulator)
        self.move_block = MoveBlock(llm, memory, simulator)
        self.mobility_none_block = MobilityNoneBlock(llm, memory)
        self.trigger_time = 0
        self.token_consumption = 0
        # 初始化调度器
        self.dispatcher = BlockDispatcher(llm)
        # 注册所有块
        self.dispatcher.register_blocks(
            [self.place_selection_block, self.move_block, self.mobility_none_block]
        )

    async def forward(self, step, context):
        self.trigger_time += 1

        # Select the appropriate sub-block using dispatcher
        selected_block = await self.dispatcher.dispatch(step)

        # Execute the selected sub-block and get the result
        result = await selected_block.forward(step, context)  # type: ignore

        return result
