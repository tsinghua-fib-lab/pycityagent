from pycityagent.llm.llm import LLM
from pycityagent.workflow.block import Block
import random


class MobilityBlock(Block):
    def __init__(self, llm: LLM):
        super().__init__(llm)

    async def forward(self, step):
        print(f"执行移动操作: {step['intention']}")
        duration = random.randint(15, 45)  # 移动通常需要15-45分钟
        evaluation = {
            "status": "completed", 
            "details": f"移动操作成功完成，耗时{duration}分钟",
            "duration": duration
        }
        step['evaluation'] = evaluation
        print(f"移动操作完成: {evaluation['details']}")