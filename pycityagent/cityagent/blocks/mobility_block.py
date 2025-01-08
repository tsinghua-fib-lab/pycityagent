from typing import List
from .dispatcher import BlockDispatcher
from pycityagent.environment.simulator import Simulator
from pycityagent.llm.llm import LLM
from pycityagent.memory.memory import Memory
from pycityagent.workflow.block import Block
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

class PlaceSelectionBlock(Block):
    """
    选择目的地
    PlaceSelectionBlock
    """
    configurable_fields: List[str] = ["search_radius", "search_limit"]
    default_values = {
        "search_radius": 100000,
        "search_limit": 10
    }

    def __init__(self, llm: LLM, memory: Memory, simulator: Simulator):
        super().__init__("PlaceSelectionBlock", llm, memory, simulator)
        self.description = "Used to select and determine destinations for unknown locations (excluding home and workplace), such as choosing specific shopping malls, restaurants and other places"
        self.typeSelectionPrompt = FormatPrompt(PLACE_TYPE_SELECTION_PROMPT)
        self.secondTypeSelectionPrompt = FormatPrompt(PLACE_SECOND_TYPE_SELECTION_PROMPT)

        # configurable fields
        self.search_radius = 100000
        self.search_limit = 10

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
        center = await self.memory.get('position')
        center = (center['xy_position']['x'], center['xy_position']['y'])
        try:
            pois = self.simulator.map.query_pois(
                center = center,
                category_prefix = levelTwoType,
                radius=self.search_radius,
                limit=self.search_limit
            )
        except Exception as e:
            logger.warning(f"Error querying pois: {e}")
            levelTwoType = random.choice(sub_category)
            pois = self.simulator.map.query_pois(
                center = center,
                category_prefix = levelTwoType,
                radius=self.search_radius,
                limit=self.search_limit
            )
        if len(pois) > 0:
            poi = random.choice(pois)[0]
            nextPlace = (poi['name'], poi['aoi_id'])
            # 将地点信息保存到context中
            context['next_place'] = nextPlace
            # 这里应该添加选择地点的具体逻辑
            return {
                'success': True,
                'evaluation': f'Successfully selected the destination: {nextPlace}',
                'consumed_time': 5
            }
        else:
            simmap = self.simulator.map
            poi = random.choice(list(simmap.pois.values()))
            nextPlace = (poi['name'], poi['aoi_id'])
            # 将地点信息保存到context中
            context['next_place'] = nextPlace
            # 这里应该添加选择地点的具体逻辑
            return {
                'success': True,
                'evaluation': f'Successfully selected the destination: {nextPlace}',
                'consumed_time': 5
            }

class MoveBlock(Block):
    """
    移动操作
    MoveBlock
    """
    def __init__(self, llm: LLM, memory: Memory, simulator: Simulator):
        super().__init__("MoveBlock", llm, memory, simulator)
        self.description = "Used to execute specific mobility operations, such as returning home, going to work, or visiting a specific location"
        self.placeAnalysisPrompt = FormatPrompt(PLACE_ANALYSIS_PROMPT)

    async def forward(self, step, context):
        # 这里应该添加移动的具体逻辑
        agent_id = await self.memory.get("id")
        self.placeAnalysisPrompt.format(
            plan = context['plan'],
            intention = step["intention"]
        )
        response = await self.llm.atext_request(self.placeAnalysisPrompt.to_dialog()) # type: ignore
        if response == 'home':
            # 返回到家
            home = await self.memory.get('home')
            home = home['aoi_position']['aoi_id']
            nowPlace = await self.memory.get('position')
            if 'aoi_position' in nowPlace and nowPlace['aoi_position']['aoi_id'] == home:
                return {
                    'success': True,
                    'evaluation': f'Successfully returned home (already at home)',
                    'from_place': home,
                    'to_place': home,
                    'consumed_time': 0
                }
            await self.simulator.set_aoi_schedules(
                person_id=agent_id,
                target_positions=home,
            )
            return {
                'success': True,
                'evaluation': f'Successfully returned home',
                'from_place': nowPlace['aoi_position']['aoi_id'],
                'to_place': home,
                'consumed_time': 45
            }
        elif response == 'workplace':
            # 返回到工作地点
            work = await self.memory.get('work')
            work = work['aoi_position']['aoi_id']
            nowPlace = await self.memory.get('position')
            if 'aoi_position' in nowPlace and nowPlace['aoi_position']['aoi_id'] == work:
                return {
                    'success': True,
                    'evaluation': f'Successfully reached the workplace (already at the workplace)',
                    'from_place': work,
                    'to_place': work,
                    'consumed_time': 0
                }
            await self.simulator.set_aoi_schedules(
                person_id=agent_id,
                target_positions=work,
            )
            return {
                'success': True,
                'evaluation': f'Successfully reached the workplace',
                'from_place': nowPlace['aoi_position']['aoi_id'],
                'to_place': work,
                'consumed_time': 45
            }
        else:
            # 移动到其他地点
            next_place = context.get('next_place', None)
            nowPlace = await self.memory.get('position')
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
                'from_place': nowPlace['aoi_position']['aoi_id'],
                'to_place': next_place[1],
                'consumed_time': 45
            }
    
class MobilityNoneBlock(Block):
    """
    空操作
    MobilityNoneBlock
    """
    def __init__(self, llm: LLM, memory: Memory):
        super().__init__("MobilityNoneBlock", llm, memory)
        self.description = "Used to handle other cases"

    async def forward(self, step, context):
        return {
            'success': True,
            'evaluation': f'Finished executing {step["intention"]}',
            'consumed_time': 0
        }

class MobilityBlock(Block):
    place_selection_block: PlaceSelectionBlock
    move_block: MoveBlock
    mobility_none_block: MobilityNoneBlock

    def __init__(self, llm: LLM, memory: Memory, simulator: Simulator):
        super().__init__("MobilityBlock", llm, memory, simulator)
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