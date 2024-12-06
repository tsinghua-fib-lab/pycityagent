from pycityagent.llm.llm import LLM
from pycityagent.workflow.block import Block
import random


class SocialBlock(Block):
    def __init__(self, llm: LLM):
        super().__init__(llm)

    async def forward(self, step):
        print(f"执行社交操作: {step['intention']}")
        duration = random.randint(30, 90)  # 社交活动通常需要30-90分钟
        evaluation = {
            "status": "completed", 
            "details": f"社交操作成功完成，耗时{duration}分钟",
            "duration": duration
        }
        step['evaluation'] = evaluation
        print(f"社交操作完成: {evaluation['details']}")