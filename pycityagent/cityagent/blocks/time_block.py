import asyncio
from datetime import datetime
import json
from pycityagent.workflow import Block
from pycityagent.llm.llm import LLM
from pycityagent.memory import Memory
from pycityagent.environment import Simulator
from pycityagent.workflow.prompt import FormatPrompt
from .utils import clean_json_response
    
class WorkReflectionBlock(Block):
    """
    反馈工作感受
    WorkReflectionBlock
    """
    def __init__(self, llm: LLM, memory: Memory, simulator: Simulator):
        super().__init__("WorkReflectionBlock", llm, memory, simulator)
        self.description = "Feedback on work experience"

    async def forward(self):
        prompt = """
You are a {gender}, your consumption level is {consumption} and your education level is {education}.
Today's working experience:
{working_experience}

How is your feeling of work today?

Your answer should be one of the following:
- excellent
- good
- soso
- bad
- very bad
Answer in JSON format:
{{
    "evaluation": "good",
}}
"""
        prompt = FormatPrompt(prompt)
        prompt.format(
            **{key: await self.memory.get(key) for key in prompt.variables}
        )
        evaluation = await self.llm.atext_request(prompt.to_dialog(), timeout=300)
        evaluation = clean_json_response(evaluation)
        try:
            evaluation = json.loads(evaluation)
        except Exception as e:
            evaluation = {'evaluation': 'soso'}
        if evaluation['evaluation'] == 'excellent':
            safe_improve = 0.2
        elif evaluation['evaluation'] == 'good':
            safe_improve = 0.1
        elif evaluation['evaluation'] == 'soso':
            safe_improve = 0.0
        elif evaluation['evaluation'] == 'bad':
            safe_improve = -0.1
        elif evaluation['evaluation'] == 'very bad':
            safe_improve = -0.2
        else:
            safe_improve = 0.0

        needs = await self.memory.get("needs")
        needs['safe'] += safe_improve
        await self.memory.update("needs", needs)
        await self.memory.update("working_experience", [])
        return


class TimeBlock(Block):
    """固定时间trigger的工作流"""
    def __init__(self, llm: LLM, memory: Memory, simulator: Simulator):
        super().__init__(name="time_block", llm=llm, memory=memory, simulator=simulator)
        self.blocks = []
        self.work_reflection_block = WorkReflectionBlock(llm, memory, simulator)
        self.blocks.append((self.work_reflection_block, self.str_to_time('23:59:59'))) # end of day
        self.last_check_time = None
        self.trigger_time = 0
        self.token_consumption = 0

    def str_to_time(self, time_str: str):
        time_obj = datetime.strptime(time_str, '%H:%M:%S')
        return time_obj.hour * 3600 + time_obj.minute * 60 + time_obj.second

    async def blocks_to_trigger(self):
        trigger_blocks = []
        now_time = await self.simulator.get_time(format_time=True)
        now_time = self.str_to_time(now_time)
        if self.last_check_time is None:
            self.last_check_time = now_time
        else:
            whether_cross_day = True if now_time < self.last_check_time else False
            for block, trigger_time in self.blocks:
                if whether_cross_day and trigger_time > self.last_check_time:
                    trigger_blocks.append(block)
                elif not whether_cross_day and trigger_time > self.last_check_time and trigger_time <= now_time:
                    trigger_blocks.append(block)
            self.last_check_time = now_time
        return trigger_blocks

    async def forward(self):
        while True:
            if len(self.blocks) == 0:
                await asyncio.sleep(30)
                continue
            trigger_blocks = await self.blocks_to_trigger()
            if len(trigger_blocks) == 0:
                await asyncio.sleep(30)
                continue
            self.trigger_time += 1
            consumption_start = self.llm.prompt_tokens_used + self.llm.completion_tokens_used
            tasks = []
            for block in trigger_blocks:
                tasks.append(block.forward())
            await asyncio.gather(*tasks)
            consumption_end = self.llm.prompt_tokens_used + self.llm.completion_tokens_used
            self.token_consumption += consumption_end - consumption_start