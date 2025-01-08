from examples.cityagent.blocks.dispatcher import BlockDispatcher
from examples.cityagent.utils import event2poi_gravity, getDirectEventID
from pycityagent.environment.simulator import Simulator
from pycityagent.llm.llm import LLM
from pycityagent.memory.memory import Memory
from pycityagent.workflow.block import Block
import random
import numpy as np

from pycityagent.workflow.prompt import FormatPrompt
from pycityagent.tools import GetMap

PLACE_TYPE_SELECTION_PROMPT = """
作为一个智能决策系统，请从用户输入的需求中判断其需要前往的地点类型。
用户需求: {intention}
你的输出只能从Please select from ['eat', 'have breakfast', 'have lunch', 'have dinner', 'do shopping', 'do sports', 'excursion', 'leisure or entertainment', 'medical treatment', 'handle the trivialities of life', 'banking and financial services', 'government and political services', 'cultural institutions and events']中选择一个输出，输出中不能包含任何额外的文本或解释。
"""

PLACE_ANALYSIS_PROMPT = """
作为一个智能分析系统，请从用户输入的需求中判断其需要前往的地点。
用户需求: {intention}

你的输出只能从['home', 'workplace', 'other']中选择一个输出，输出中不能包含任何额外的文本或解释。
"""


class PlaceSelectionBlock(Block):
    """
    选择目的地
    PlaceSelectionBlock
    """

    def __init__(self, llm: LLM, memory: Memory, simulator: Simulator):
        super().__init__("PlaceSelectionBlock", llm)
        self.memory = memory
        self.simulator = simulator
        self.description = "用于选择和确定目的地的位置，比如选择具体的商场、餐厅等地点"
        self.typeSelectionPrompt = FormatPrompt(PLACE_TYPE_SELECTION_PROMPT)

    async def forward(self, step, context):
        self.typeSelectionPrompt.format(intention=step["intention"])
        intention = await self.llm.atext_request(self.typeSelectionPrompt.to_dialog())  # type: ignore
        simmap = self.simulator.map
        poi = random.choice(list(simmap.pois.values()))
        nextPlace = (poi["name"], poi["aoi_id"])
        # 将地点信息保存到context中
        context["next_place"] = nextPlace
        # 这里应该添加选择地点的具体逻辑
        return {
            "success": True,
            "evaluation": f"成功选择了目的地: {nextPlace}",
            "consumed_time": 5,
        }


class MoveBlock(Block):
    """
    移动操作
    MoveBlock
    """

    def __init__(self, llm: LLM, memory: Memory, simulator: Simulator):
        super().__init__("MoveBlock", llm)
        self.memory = memory
        self.simulator = simulator
        self.description = "用于执行具体的移动操作, 例如回家，去工作，前往某地等"
        self.placeAnalysisPrompt = FormatPrompt(PLACE_ANALYSIS_PROMPT)

    async def forward(self, step, context):
        # 这里应该添加移动的具体逻辑
        agent_id = await self.memory.get("id")
        self.placeAnalysisPrompt.format(intention=step["intention"])
        response = await self.llm.atext_request(self.placeAnalysisPrompt.to_dialog())  # type: ignore
        if response == "home":
            # 返回到家
            home = await self.memory.get("home")
            home = home["aoi_position"]["aoi_id"]
            nowPlace = await self.memory.get("position")
            if (
                "aoi_position" in nowPlace
                and nowPlace["aoi_position"]["aoi_id"] == home
            ):
                return {
                    "success": True,
                    "evaluation": f"成功回到家(本来就在家中)",
                    "consumed_time": 0,
                }
            await self.simulator.set_aoi_schedules(
                person_id=agent_id,
                target_positions=home,
            )
            return {"success": True, "evaluation": f"成功回到家", "consumed_time": 45}
        elif response == "workplace":
            # 返回到工作地点
            work = await self.memory.get("work")
            work = work["aoi_position"]["aoi_id"]
            await self.simulator.set_aoi_schedules(
                person_id=agent_id,
                target_positions=work,
            )
            return {
                "success": True,
                "evaluation": f"成功到达工作地",
                "consumed_time": 45,
            }
        else:
            # 移动到其他地点
            next_place = context.get("next_place", None)
            if next_place != None:
                await self.simulator.set_aoi_schedules(
                    person_id=agent_id,
                    target_positions=next_place[1],
                )
            else:
                r_aoi = random.choice(list(self.simulator.map.aois.values()))
                r_poi = random.choice(r_aoi["poi_ids"].values())
                next_place = (r_poi["name"], r_aoi["id"])
                await self.simulator.set_aoi_schedules(
                    person_id=agent_id,
                    target_positions=next_place[1],
                )
            return {
                "success": True,
                "evaluation": f"成功到达目的地: {next_place}",
                "consumed_time": 45,
            }


class MobilityNoneBlock(Block):
    """
    空操作
    MobilityNoneBlock
    """

    def __init__(self, llm: LLM, memory: Memory):
        super().__init__("MobilityNoneBlock", llm)
        self.memory = memory
        self.description = "用于处理其他情况"

    async def forward(self, step, context):
        return {
            "success": True,
            "evaluation": f'完成执行{step["intention"]}',
            "consumed_time": 0,
        }


class MobilityBlock(Block):
    def __init__(self, llm: LLM, memory: Memory, simulator: Simulator):
        super().__init__("MobilityBlock", llm)
        self.memory = memory
        self.simulator = simulator
        # 初始化所有块
        self.place_selection_block = PlaceSelectionBlock(llm, memory, simulator)
        self.move_block = MoveBlock(llm, memory, simulator)
        self.mobility_none_block = MobilityNoneBlock(llm, memory)
        # 初始化调度器
        self.dispatcher = BlockDispatcher(llm)
        # 注册所有块
        self.dispatcher.register_blocks(
            [self.place_selection_block, self.move_block, self.mobility_none_block]
        )

    async def forward(self, step, context):
        # Select the appropriate sub-block using dispatcher
        selected_block = await self.dispatcher.dispatch(step)

        # Execute the selected sub-block and get the result
        result = await selected_block.forward(step, context)  # type: ignore

        return result
