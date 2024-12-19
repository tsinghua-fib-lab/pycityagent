from examples.cityagent.blocks.dispatcher import BlockDispatcher
from pycityagent.llm.llm import LLM
from pycityagent.workflow.block import Block
import random
from pycityagent.memory import Memory


class SleepBlock(Block):
    def __init__(self, llm: LLM, memory: Memory):
        super().__init__("SleepBlock", llm)
        self.description = "进行睡眠"
        self.memory = memory

    async def forward(self, step, context):
        return {
            "success": True,
            "evaluation": f"进行睡眠，睡眠时长为7小时",
            "consumed_time": 7 * 60,
        }


class WorkBlock(Block):
    def __init__(self, llm: LLM, memory: Memory):
        super().__init__("WorkBlock", llm)
        self.description = "进行工作"
        self.memory = memory

    async def forward(self, step, context):
        return {
            "success": True,
            "evaluation": f"进行工作，工作时长为4小时",
            "consumed_time": 4 * 60,
        }


class OtherNoneBlock(Block):
    """
    空操作
    OtherNoneBlock
    """

    def __init__(self, llm: LLM, memory: Memory):
        super().__init__("OtherNoneBlock", llm)
        self.memory = memory
        self.description = "用于处理其他情况"

    async def forward(self, step, context):
        return {
            "success": True,
            "evaluation": f'完成执行{step["intention"]}',
            "consumed_time": 0,
        }


class OtherBlock(Block):
    def __init__(self, llm: LLM, memory: Memory):
        super().__init__("OtherBlock", llm)
        self.memory = memory
        # 初始化所有块
        self.sleep_block = SleepBlock(llm, memory)
        self.work_block = WorkBlock(llm, memory)
        self.other_none_block = OtherNoneBlock(llm, memory)
        # 初始化调度器
        self.dispatcher = BlockDispatcher(llm)
        # 注册所有块
        self.dispatcher.register_blocks(
            [self.sleep_block, self.work_block, self.other_none_block]
        )

    async def forward(self, step, context):
        # Select the appropriate sub-block using dispatcher
        selected_block = await self.dispatcher.dispatch(step)

        # Execute the selected sub-block and get the result
        result = await selected_block.forward(step, context)  # type: ignore

        return result
