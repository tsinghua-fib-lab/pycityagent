import json
import random

from .dispatcher import BlockDispatcher
from pycityagent.llm.llm import LLM
from pycityagent.workflow.block import Block
from pycityagent.memory import Memory
from pycityagent.workflow.prompt import FormatPrompt
from .utils import clean_json_response, TIME_ESTIMATE_PROMPT
import logging
logger = logging.getLogger("pycityagent")

class SleepBlock(Block):
    def __init__(self, llm: LLM, memory: Memory):
        super().__init__("SleepBlock", llm=llm, memory=memory)
        self.description = "Sleep"
        self.guidance_prompt = FormatPrompt(template=TIME_ESTIMATE_PROMPT)

    async def forward(self, step, context):
        self.guidance_prompt.format(
            plan=context['plan'],
            intention=step['intention'],
            emotion_types=await self.memory.status.get("emotion_types"),
        )
        result = await self.llm.atext_request(self.guidance_prompt.to_dialog())
        result = clean_json_response(result)
        node_id = await self.memory.stream.add_other(description=f"I slept")
        try:
            result = json.loads(result)
            return {
                'success': True,
                'evaluation': f'Sleep: {step["intention"]}',
                'consumed_time': result['time'],
                'node_id': node_id
            }
        except Exception as e:
            logger.warning(f"解析时间评估响应时发生错误: {str(e)}, 原始结果: {result}")
            return {
                'success': True,
                'evaluation': f'Sleep: {step["intention"]}',
                'consumed_time': random.randint(1, 10)*60,
                'node_id': node_id
            }
    
class OtherNoneBlock(Block):
    """
    空操作
    OtherNoneBlock
    """
    def __init__(self, llm: LLM, memory: Memory):
        super().__init__("OtherNoneBlock", llm=llm, memory=memory)
        self.description = "Used to handle other cases"
        self.guidance_prompt = FormatPrompt(template=TIME_ESTIMATE_PROMPT)

    async def forward(self, step, context):
        self.guidance_prompt.format(
            plan=context['plan'],
            intention=step['intention'],
            emotion_types=await self.memory.status.get("emotion_types"),
        )
        result = await self.llm.atext_request(self.guidance_prompt.to_dialog())
        result = clean_json_response(result)
        node_id = await self.memory.stream.add_other(description=f"I {step['intention']}")
        try:
            result = json.loads(result)
            return {
                'success': True,
                'evaluation': f'Finished executing {step["intention"]}',
                'consumed_time': result['time'],
                'node_id': node_id
            }
        except Exception as e:
            logger.warning(f"解析时间评估响应时发生错误: {str(e)}, 原始结果: {result}")
            return {
                'success': True,
                'evaluation': f'Finished executing {step["intention"]}',
                'consumed_time': random.randint(1, 180),
                'node_id': node_id
            }
    

class OtherBlock(Block):
    sleep_block: SleepBlock
    other_none_block: OtherNoneBlock

    def __init__(self, llm: LLM, memory: Memory):
        super().__init__("OtherBlock", llm=llm, memory=memory)
        # 初始化所有块
        self.sleep_block = SleepBlock(llm, memory)
        self.other_none_block = OtherNoneBlock(llm, memory)
        self.trigger_time = 0
        self.token_consumption = 0
        # 初始化调度器
        self.dispatcher = BlockDispatcher(llm)
        # 注册所有块
        self.dispatcher.register_blocks([self.sleep_block, self.other_none_block])

    async def forward(self, step, context):
        self.trigger_time += 1
        consumption_start = self.llm.prompt_tokens_used + self.llm.completion_tokens_used

        # Select the appropriate sub-block using dispatcher
        selected_block = await self.dispatcher.dispatch(step)
        
        # Execute the selected sub-block and get the result
        result = await selected_block.forward(step, context) # type: ignore
        
        consumption_end = self.llm.prompt_tokens_used + self.llm.completion_tokens_used
        self.token_consumption += consumption_end - consumption_start
        
        return result