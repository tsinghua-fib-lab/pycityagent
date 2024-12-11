from pycityagent.llm.llm import LLM
from pycityagent.workflow.block import Block
import random
from pycityagent.memory import Memory


class SocialBlock(Block):
    def __init__(self, llm: LLM, memory: Memory):
        super().__init__("SocialBlock", llm)
        self.memory = memory

    async def forward(self, step, context):
        duration = random.randint(30, 90)  # 社交活动通常需要30-90分钟
        return {
            'success': True,
            'evaluation': f'完成执行{step["intention"]}',
            'consumed_time': duration
        }