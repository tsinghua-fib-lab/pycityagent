from pycityagent.llm.llm import LLM
from pycityagent.workflow.block import Block
import random
from pycityagent.memory import Memory

class CognitionBlock(Block):
    def __init__(self, llm: LLM, memory: Memory):
        super().__init__(llm)
        self.memory = memory

    async def forward(self, step, context):
        print(f"执行认知操作: {step['intention']}")
        duration = random.randint(10, 30)  # 认知活动通常需要10-30分钟
        return {
            'success': True,
            'evaluation': f'完成执行{step["intention"]}',
            'consumed_time': duration
        }