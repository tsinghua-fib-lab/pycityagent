import json
import random
from typing import Dict, List
from pycityagent.environment.simulator import Simulator
from pycityagent.workflow import Block
from pycityagent.llm import LLM
from pycityagent.memory import Memory
from pycityagent.workflow.prompt import FormatPrompt
import logging

logger = logging.getLogger("pycityagent")

GUIDANCE_SELECTION_PROMPT = """As an intelligent agent's decision system, please select the most suitable option from the following choices to satisfy the current need.
The Environment will influence the choice of steps.

Current weather: {weather}
Current temperature: {temperature}

Current need: Need to satisfy {current_need}
Available options: {options}
Current location: {current_location}
Current time: {current_time}
Your emotion: {emotion_types}
Your thought: {thought}

Please evaluate and select the most appropriate option based on these three dimensions:
1. Attitude: Personal preference and evaluation of the option
2. Subjective Norm: Social environment and others' views on this behavior
3. Perceived Control: Difficulty and controllability of executing this option

Please return the evaluation results in JSON format (Do not return any other text):
{{
    "selected_option": "Select the most suitable option from available options",
    "evaluation": {{
        "attitude": "Attitude score for the option (0-1)",
        "subjective_norm": "Subjective norm score (0-1)", 
        "perceived_control": "Perceived control score (0-1)",
        "reasoning": "Specific reasons for selecting this option"
    }}
}}
"""

DETAILED_PLAN_PROMPT = """Generate specific execution steps based on the selected guidance plan. The Environment will influence the choice of steps.

Current weather: {weather}
Current temperature: {temperature}

Selected plan: {selected_option}
Current location: {current_location} 
Current time: {current_time}
Your emotion: {emotion_types}
Your thought: {thought}

Please generate specific execution steps and return in JSON format:
{{
    "plan": {{
        "target": "Specific goal",
        "steps": [
            {{
                "intention": "Specific intention",
                "type": "Step type"
            }}
        ]
    }}
}}

Notes:
1. type can only be one of these four: mobility, social, economy, other
    1.1 mobility: Decisions or behaviors related to large-scale spatial movement, such as location selection, going to a place, etc.
    1.2 social: Decisions or behaviors related to social interaction, such as finding contacts, chatting with friends, etc.
    1.3 economy: Decisions or behaviors related to shopping, work, etc.
    1.4 other: Other types of decisions or behaviors, such as small-scale activities, learning, resting, entertainment, etc.
2. steps should only include steps necessary to fulfill the target (limited to {max_plan_steps} steps)
3. intention in each step should be concise and clear

Example outputs (Do not return any other text):
{{
    "plan": {{
        "target": "Eat at home",
        "steps": [
            {{
                "intention": "Return home from current location",
                "type": "mobility"
            }},
            {{
                "intention": "Cook food",
                "type": "other"
            }},
            {{
                "intention": "Have meal",
                "type": "other"
            }}
        ]
    }}
}}

{{
    "plan": {{
        "target": "Eat outside",
        "steps": [
            {{
                "intention": "Select restaurant",
                "type": "mobility"
            }},
            {{
                "intention": "Go to restaurant",
                "type": "mobility"
            }},
            {{
                "intention": "Order food",
                "type": "economy"
            }},
            {{
                "intention": "Have meal",
                "type": "other"
            }}
        ]
    }}
}}

{{
    "plan": {{
        "target": "Offline social",
        "steps": [
            {{
                "intention": "Contact friends to arrange meeting place",
                "type": "social"
            }},
            {{
                "intention": "Go to meeting place",
                "type": "mobility"
            }},
            {{
                "intention": "Chat with friends",
                "type": "social"
            }}
        ]
    }}
}}

{{
    "plan": {{
        "target": "Work",
        "steps": [
            {{
                "intention": "Go to workplace",
                "type": "mobility"
            }},
            {{
                "intention": "Work",
                "type": "other"
            }}
        ]
    }}
}}
"""

class PlanBlock(Block):
    configurable_fields: List[str] = ["max_plan_steps"]
    default_values = {
        "max_plan_steps": 6
    }
    fields_description = {
        "max_plan_steps": "The maximum number of steps in a plan"
    }

    def __init__(self, llm: LLM, memory: Memory, simulator: Simulator):
        super().__init__("PlanBlock", llm=llm, memory=memory, simulator=simulator)
        self.guidance_prompt = FormatPrompt(template=GUIDANCE_SELECTION_PROMPT)
        self.detail_prompt = FormatPrompt(template=DETAILED_PLAN_PROMPT)
        self.trigger_time = 0
        self.token_consumption = 0
        self.guidance_options = {
            "hungry": ['Eat at home', 'Eat outside'],
            "tired": ['Sleep', 'Take a nap'],
            "safe": ['Work'],
            "social": ['Online social', 'Shopping'],
            "whatever": ['Learning', 'Entertainment', 'Hang out', 'Exercise']
        }

        # configurable fields
        self.max_plan_steps = 6

    async def select_guidance(self, current_need: str) -> Dict:
        """Select guidance plan"""
        position_now = await self.memory.status.get("position")
        home_location = await self.memory.status.get("home")
        work_location = await self.memory.status.get("work")
        current_location = "Out"
        if 'aoi_position' in position_now and position_now['aoi_position'] == home_location['aoi_position']:
            current_location = "At home"
        elif 'aoi_position' in position_now and position_now['aoi_position'] == work_location['aoi_position']:
            current_location = "At workplace"
        current_time = await self.simulator.get_time(format_time=True)
        environment = await self.memory.status.get("environment")
        options = self.guidance_options.get(current_need, [])
        self.guidance_prompt.format(
            weather=self.simulator.sence("weather"),
            temperature=self.simulator.sence("temperature"),
            current_need=current_need,
            options=options,
            current_location=current_location,
            current_time=current_time,
            environment=environment,
            emotion_types=await self.memory.status.get("emotion_types"),
            thought=await self.memory.status.get("thought")
        )

        response = await self.llm.atext_request(
            self.guidance_prompt.to_dialog()
        ) # type: ignore

        try:
            result = json.loads(self.clean_json_response(response)) # type: ignore
            return result
        except Exception as e:
            logger.warning(f"Error parsing guidance selection response: {str(e)}")
            return None # type: ignore

    async def generate_detailed_plan(self, current_need: str, selected_option: str) -> Dict:
        """Generate detailed execution plan"""
        position_now = await self.memory.status.get("position")
        home_location = await self.memory.status.get("home")
        work_location = await self.memory.status.get("work")
        current_location = "Out"
        if 'aoi_position' in position_now and position_now['aoi_position'] == home_location['aoi_position']:
            current_location = "At home"
        elif 'aoi_position' in position_now and position_now['aoi_position'] == work_location['aoi_position']:
            current_location = "At workplace"
        current_time = await self.simulator.get_time(format_time=True)
        environment = await self.memory.status.get("environment")
        self.detail_prompt.format(
            weather=self.simulator.sence("weather"),
            temperature=self.simulator.sence("temperature"),
            selected_option=selected_option,
            current_location=current_location,
            current_time=current_time,
            environment=environment,
            emotion_types=await self.memory.status.get("emotion_types"),
            thought=await self.memory.status.get("thought"),
            max_plan_steps=self.max_plan_steps
        )

        response = await self.llm.atext_request(
            self.detail_prompt.to_dialog()
        )

        try:
            result = json.loads(self.clean_json_response(response)) # type: ignore
            return result
        except Exception as e:
            logger.warning(f"Error parsing detailed plan: {str(e)}")
            return None # type: ignore

    async def forward(self):
        self.trigger_time += 1
        consumption_start = self.llm.prompt_tokens_used + self.llm.completion_tokens_used
        
        # Step 1: Select guidance plan
        current_need = await self.memory.status.get("current_need")
        guidance_result = await self.select_guidance(current_need)
        if not guidance_result:
            return

        # Step 2: Generate detailed plan
        detailed_plan = await self.generate_detailed_plan(
            current_need, 
            guidance_result["selected_option"]
        )
        
        if not detailed_plan or "plan" not in detailed_plan:
            await self.memory.status.update("current_plan", [])
            await self.memory.status.update("current_step", {"intention": "", "type": ""})
            return
        
        # Step 3: Update plan and current step
        steps = detailed_plan["plan"]["steps"]
        for step in steps:
            step["evaluation"] = {"status": "pending", "details": ""}

        plan = {
            "target": detailed_plan["plan"]["target"],
            "steps": steps,
            "completed": False,
            "failed": False,
            "stream_nodes": [],
            "guidance": guidance_result  # Save the evaluation result of the plan selection
        }
        formated_steps = "\n".join([f"{i}. {step['intention']}" for i, step in enumerate(plan['steps'], 1)])
        formated_plan = f"""
Overall Target: {plan['target']}
Execution Steps: \n{formated_steps}
        """
        plan['start_time'] = await self.simulator.get_time(format_time=True)
        await self.memory.status.update("current_plan", plan)
        await self.memory.status.update("current_step", steps[0] if steps else {"intention": "", "type": ""})
        await self.memory.status.update("execution_context", {'plan': formated_plan})

        consumption_end = self.llm.prompt_tokens_used + self.llm.completion_tokens_used
        self.token_consumption += consumption_end - consumption_start

    def clean_json_response(self, response: str) -> str:
        """Clean special characters in LLM response"""
        response = response.replace('```json', '').replace('```', '')
        return response.strip() 
