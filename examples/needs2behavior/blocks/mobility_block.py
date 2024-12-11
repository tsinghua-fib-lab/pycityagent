from examples.needs2behavior.blocks.dispatcher import BlockDispatcher
from pycityagent.llm.llm import LLM
from pycityagent.memory.memory import Memory
from pycityagent.workflow.block import Block
import random

class PlaceSelectionBlock(Block):
    """
    选择目的地
    PlaceSelectionBlock
    """
    def __init__(self, llm: LLM, memory: Memory):
        super().__init__(llm)
        self.memory = memory
        self.description = "用于选择和确定目的地的位置，比如选择具体的商场、餐厅等地点"

    async def forward(self, step, context):
        # 这里应该添加选择地点的具体逻辑
        return {
            'success': True,
            'evaluation': '成功选择了目的地',
            'consumed_time': random.randint(5, 15)
        }

class MoveBlock(Block):
    """
    移动操作
    MoveBlock
    """
    def __init__(self, llm: LLM, memory: Memory):
        super().__init__(llm)
        self.memory = memory
        self.description = "用于执行具体的移动操作"

    async def forward(self, step, context):
        # 这里应该添加移动的具体逻辑
        return {
            'success': True,
            'evaluation': '成功到达目的地',
            'consumed_time': random.randint(15, 45)
        }

class MobilityNoneBlock(Block):
    """
    空操作
    MobilityNoneBlock
    """
    def __init__(self, llm: LLM, memory: Memory):
        super().__init__(llm)
        self.memory = memory
        self.description = "用于处理其他情况"

    async def forward(self, step, context):
        return {
            'success': True,
            'evaluation': f'完成执行{step["intention"]}',
            'consumed_time': 0
        }

class MobilityBlock(Block):
    def __init__(self, llm: LLM, memory: Memory):
        super().__init__(llm)
        self.memory = memory
        # 初始化所有块
        self.place_selection_block = PlaceSelectionBlock(llm, memory)
        self.move_block = MoveBlock(llm, memory)
        self.mobility_none_block = MobilityNoneBlock(llm, memory)
        # 初始化调度器
        self.dispatcher = BlockDispatcher(llm)
        # 注册所有块
        self.dispatcher.register_blocks([self.place_selection_block, self.move_block, self.mobility_none_block])

    async def forward(self, step, context):        
        # Select the appropriate sub-block using dispatcher
        selected_block = await self.dispatcher.dispatch(step)
        
        # Execute the selected sub-block and get the result
        result = await selected_block.forward(step, context)
        
        return result