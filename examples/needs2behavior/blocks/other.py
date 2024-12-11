from pycityagent.llm.llm import LLM
from pycityagent.workflow.block import Block
import random
from pycityagent.memory import Memory

class OtherBlock(Block):
    def __init__(self, llm: LLM, memory: Memory):
        super().__init__(llm)
        self.memory = memory

    async def forward(self, step, context):
        duration = random.randint(5, 20)  # 基础行为通常需要5-20分钟
        return {
            'success': True,
            'evaluation': f'完成执行{step["intention"]}',
            'consumed_time': duration
        }