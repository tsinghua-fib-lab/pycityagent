from pycityagent.llm.llm import LLM
from pycityagent.workflow.block import Block
import random


class EconomyBlock(Block):
    def __init__(self, llm: LLM):
        super().__init__(llm)

    async def forward(self, step):
        print(f"执行经济操作: {step['intention']}")
        duration = random.randint(10, 30)  # 经济活动通常需要10-30分钟
        evaluation = {
            "status": "completed", 
            "details": f"经济操作成功完成，耗时{duration}分钟",
            "duration": duration
        }
        step['evaluation'] = evaluation
        print(f"经济操作完成: {evaluation['details']}")