from pycityagent.llm.llm import LLM
from pycityagent.workflow.block import Block
import random
from pycityagent.memory import Memory

class CognitionBlock(Block):
    def __init__(self, llm: LLM, memory: Memory):
        super().__init__("CognitionBlock", llm)
        self.memory = memory

    async def forward(self):
        print(f"执行认知更新")