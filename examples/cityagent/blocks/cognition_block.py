import random

from pycityagent.llm.llm import LLM
from pycityagent.memory import Memory
from pycityagent.workflow.block import Block


class CognitionBlock(Block):
    def __init__(self, llm: LLM, memory: Memory):
        super().__init__("CognitionBlock", llm)
        self.set_memory(memory)

    async def forward(self):
        print(f"执行认知更新")
