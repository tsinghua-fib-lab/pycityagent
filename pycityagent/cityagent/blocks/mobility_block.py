import math
from typing import List
from .dispatcher import BlockDispatcher
from pycityagent.environment.simulator import Simulator
from pycityagent.llm import LLM
from pycityagent.memory import Memory
from pycityagent.workflow.block import Block
import numpy as np
from operator import itemgetter
import random
import logging
logger = logging.getLogger("pycityagent")
from pycityagent.workflow.prompt import FormatPrompt

PLACE_TYPE_SELECTION_PROMPT = """
As an intelligent decision system, please determine the type of place the user needs to visit based on their input requirement.
User Plan: {plan}
User requirement: {intention}
Your output must be a single selection from {poi_category} without any additional text or explanation.
"""

PLACE_SECOND_TYPE_SELECTION_PROMPT = """
As an intelligent decision system, please determine the type of place the user needs to visit based on their input requirement.
User Plan: {plan}
User requirement: {intention}
Your output must be a single selection from {poi_category} without any additional text or explanation.
"""

PLACE_ANALYSIS_PROMPT = """
As an intelligent analysis system, please determine the type of place the user needs to visit based on their input requirement.
User Plan: {plan}
User requirement: {intention}

Your output must be a single selection from ['home', 'workplace', 'other'] without any additional text or explanation.
"""

RADIUS_PROMPT = """As an intelligent decision system, please determine the maximum travel radius (in meters) based on the current emotional state.

Current weather: {weather}
Current temperature: {temperature}
Your current emotion: {emotion_types}
Your current thought: {thought}

Please analyze how these emotions would affect travel willingness and return only a single integer number between 3000-100000 representing the maximum travel radius in meters. A more positive emotional state generally leads to greater willingness to travel further.

Return only the integer number without any additional text or explanation."""

def gravity_model(pois):
    N = len(pois)
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
                distanceProb.append(
                    1 / (math.sqrt(distance))
                )
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
    default_values = {
        "search_limit": 10000
    }

    def __init__(self, llm: LLM, memory: Memory, simulator: Simulator):
        super().__init__("PlaceSelectionBlock", llm=llm, memory=memory, simulator=simulator)
        self.description = "Used to select and determine destinations for unknown locations (excluding home and workplace), such as choosing specific shopping malls, restaurants and other places"
        self.typeSelectionPrompt = FormatPrompt(PLACE_TYPE_SELECTION_PROMPT)
        self.secondTypeSelectionPrompt = FormatPrompt(PLACE_SECOND_TYPE_SELECTION_PROMPT)
        self.radiusPrompt = FormatPrompt(RADIUS_PROMPT)
        # configurable fields
        self.search_limit = 10000

    async def forward(self, step, context):
        self.typeSelectionPrompt.format(
            plan = context['plan'],
            intention = step['intention'],
            poi_category = list(self.simulator.poi_cate.keys())
        )
        levelOneType = await self.llm.atext_request(self.typeSelectionPrompt.to_dialog()) # type: ignore
        try:
            sub_category = self.simulator.poi_cate[levelOneType]
        except Exception as e:
            logger.warning(f"Wrong type of poi, raw response: {levelOneType}")
            levelOneType = random.choice(list(self.simulator.poi_cate.keys()))
            sub_category = self.simulator.poi_cate[levelOneType]
        self.secondTypeSelectionPrompt.format(
            plan = context['plan'],
            intention = step['intention'],
            poi_category = sub_category
        )
        levelTwoType = await self.llm.atext_request(self.secondTypeSelectionPrompt.to_dialog()) # type: ignore
        center = await self.memory.status.get('position')
        center = (center['xy_position']['x'], center['xy_position']['y'])
        self.radiusPrompt.format(
            emotion_types=await self.memory.status.get("emotion_types"),
            thought=await self.memory.status.get("thought"),
            weather=self.simulator.sence("weather"),
            temperature=self.simulator.sence("temperature")
        )
        radius = int(await self.llm.atext_request(self.radiusPrompt.to_dialog())) # type: ignore
        try:
            pois = self.simulator.map.query_pois(
                center = center,
                category_prefix = levelTwoType,
                radius=radius,
                limit=self.search_limit
            )
        except Exception as e:
            logger.warning(f"Error querying pois: {e}")
            levelTwoType = random.choice(sub_category)
            pois = self.simulator.map.query_pois(
                center = center,
                category_prefix = levelTwoType,
                radius=radius,
                limit=self.search_limit
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
            context['next_place'] = nextPlace
            node_id = await self.memory.stream.add_mobility(description=f"For {step['intention']}, I selected the destination: {nextPlace}")
            return {
                'success': True,
                'evaluation': f'Successfully selected the destination: {nextPlace}',
                'consumed_time': 5,
                'node_id': node_id
            }
        else:
            simmap = self.simulator.map
            poi = random.choice(list(simmap.pois.values()))
            nextPlace = (poi['name'], poi['aoi_id'])
            # save the destination to context
            context['next_place'] = nextPlace
            node_id = await self.memory.stream.add_mobility(description=f"For {step['intention']}, I selected the destination: {nextPlace}")
            return {
                'success': True,
                'evaluation': f'Successfully selected the destination: {nextPlace}',
                'consumed_time': 5,
                'node_id': node_id
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
        # 这里应该添加移动的具体逻辑
        agent_id = await self.memory.status.get("id")
        self.placeAnalysisPrompt.format(
            plan = context['plan'],
            intention = step["intention"]
        )
        number_poi_visited = await self.memory.status.get("number_poi_visited")
        number_poi_visited += 1
        await self.memory.status.update("number_poi_visited", number_poi_visited)
        response = await self.llm.atext_request(self.placeAnalysisPrompt.to_dialog()) # type: ignore
        if response == 'home':
            # 返回到家
            home = await self.memory.status.get('home')
            home = home['aoi_position']['aoi_id']
            nowPlace = await self.memory.status.get('position')
            node_id = await self.memory.stream.add_mobility(description=f"I returned home")
            if 'aoi_position' in nowPlace and nowPlace['aoi_position']['aoi_id'] == home:
                return {
                    'success': True,
                    'evaluation': f'Successfully returned home (already at home)',
                    'to_place': home,
                    'consumed_time': 0,
                    'node_id': node_id
                }
            await self.simulator.set_aoi_schedules(
                person_id=agent_id,
                target_positions=home,
            )
            return {
                'success': True,
                'evaluation': f'Successfully returned home',
                'to_place': home,
                'consumed_time': 45,
                'node_id': node_id
            }
        elif response == 'workplace':
            # 返回到工作地点
            work = await self.memory.status.get('work')
            work = work['aoi_position']['aoi_id']
            nowPlace = await self.memory.status.get('position')
            node_id = await self.memory.stream.add_mobility(description=f"I went to my workplace")
            if 'aoi_position' in nowPlace and nowPlace['aoi_position']['aoi_id'] == work:
                return {
                    'success': True,
                    'evaluation': f'Successfully reached the workplace (already at the workplace)',
                    'to_place': work,
                    'consumed_time': 0,
                    'node_id': node_id
                }
            await self.simulator.set_aoi_schedules(
                person_id=agent_id,
                target_positions=work,
            )
            return {
                'success': True,
                'evaluation': f'Successfully reached the workplace',
                'to_place': work,
                'consumed_time': 45,
                'node_id': node_id
            }
        else:
            # 移动到其他地点
            next_place = context.get('next_place', None)
            nowPlace = await self.memory.status.get('position')
            node_id = await self.memory.stream.add_mobility(description=f"I went to {next_place}")
            if next_place != None:
                await self.simulator.set_aoi_schedules(
                    person_id=agent_id,
                    target_positions=next_place[1],
                )
            else:
                while True:
                    r_aoi = random.choice(list(self.simulator.map.aois.values()))
                    if len(r_aoi['poi_ids']) > 0:
                        r_poi = random.choice(r_aoi['poi_ids'])
                        break
                poi = self.simulator.map.pois[r_poi]
                next_place = (poi['name'], poi['aoi_id'])
                await self.simulator.set_aoi_schedules(
                    person_id=agent_id,
                    target_positions=next_place[1],
                )
            return {
                'success': True,
                'evaluation': f'Successfully reached the destination: {next_place}',
                'to_place': next_place[1],
                'consumed_time': 45,
                'node_id': node_id
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
        node_id = await self.memory.stream.add_mobility(description=f"I finished {step['intention']}")
        return {
            'success': True,
            'evaluation': f'Finished executing {step["intention"]}',
            'consumed_time': 0,
            'node_id': node_id
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
        self.dispatcher.register_blocks([self.place_selection_block, self.move_block, self.mobility_none_block])

    async def forward(self, step, context):       
        self.trigger_time += 1
        consumption_start = self.llm.prompt_tokens_used + self.llm.completion_tokens_used

        # Select the appropriate sub-block using dispatcher
        selected_block = await self.dispatcher.dispatch(step)
        
        # Execute the selected sub-block and get the result
        result = await selected_block.forward(step, context) # type: ignore

        consumption_end = self.llm.prompt_tokens_used + self.llm.completion_tokens_used
        self.token_consumption += consumption_end - consumption_start
        
        return result