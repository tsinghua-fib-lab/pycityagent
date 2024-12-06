from pycityagent.llm.llm import LLM
from pycityagent.workflow.block import Block
import random


class OtherBlock(Block):
    def __init__(self, llm: LLM):
        super().__init__(llm)

    async def forward(self, step):
        print(f"执行基础行为: {step['intention']}")
        duration = random.randint(5, 20)  # 基础行为通常需要5-20分钟
        evaluation = {
            "status": "completed", 
            "details": f"基础行为执行完成，耗时{duration}分钟",
            "duration": duration
        }
        step['evaluation'] = evaluation
        print(f"基础行为完成: {evaluation['details']}")