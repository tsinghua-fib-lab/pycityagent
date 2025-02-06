import json
import logging
import random
from typing import Dict, List

import ray

from agentsociety.environment.simulator import Simulator
from agentsociety.llm import LLM
from agentsociety.memory import Memory
from agentsociety.workflow import Block
from agentsociety.workflow.prompt import FormatPrompt
from .utils import clean_json_response
logger = logging.getLogger("agentsociety")

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

Please response in json format (Do not return any other text), example:
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

Notes:
1. type can only be one of these four: mobility, social, economy, other
    1.1 mobility: Decisions or behaviors related to large-scale spatial movement, such as location selection, going to a place, etc.
    1.2 social: Decisions or behaviors related to social interaction, such as finding contacts, chatting with friends, etc.
    1.3 economy: Decisions or behaviors related to shopping, work, etc.
    1.4 other: Other types of decisions or behaviors, such as small-scale activities, learning, resting, entertainment, etc.
2. steps should only include steps necessary to fulfill the target (limited to {max_plan_steps} steps)
3. intention in each step should be concise and clear

Please response in json format (Do not return any other text), example:
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
    default_values = {"max_plan_steps": 6}
    fields_description = {"max_plan_steps": "The maximum number of steps in a plan"}

    def __init__(self, llm: LLM, memory: Memory, simulator: Simulator):
        super().__init__("PlanBlock", llm=llm, memory=memory, simulator=simulator)
        self.guidance_prompt = FormatPrompt(template=GUIDANCE_SELECTION_PROMPT)
        self.detail_prompt = FormatPrompt(template=DETAILED_PLAN_PROMPT)
        self.trigger_time = 0
        self.token_consumption = 0
        self.guidance_options = {
            "hungry": ["Eat at home", "Eat outside"],
            "tired": ["Sleep"],
            "safe": ["Go to work"],
            "social": ["Contact with friends", "Shopping"],
            "whatever": ["Contact with friends", "Hang out", "Entertainment"],
        }

        # configurable fields
        self.max_plan_steps = 6

    async def select_guidance(self, current_need: str) -> Dict:
        """Select guidance plan"""
        position_now = await self.memory.status.get("position")
        home_location = await self.memory.status.get("home")
        work_location = await self.memory.status.get("work")
        current_location = "Out"
        if (
            "aoi_position" in position_now
            and position_now["aoi_position"] == home_location["aoi_position"]
        ):
            current_location = "At home"
        elif (
            "aoi_position" in position_now
            and position_now["aoi_position"] == work_location["aoi_position"]
        ):
            current_location = "At workplace"
        current_time = await self.simulator.get_time(format_time=True)
        options = self.guidance_options.get(current_need, [])
        self.guidance_prompt.format(
            weather=self.simulator.sence("weather"),
            temperature=self.simulator.sence("temperature"),
            current_need=current_need,
            options=options,
            current_location=current_location,
            current_time=current_time,
            emotion_types=await self.memory.status.get("emotion_types"),
            thought=await self.memory.status.get("thought"),
        )

        response = await self.llm.atext_request(
            self.guidance_prompt.to_dialog(), response_format={"type": "json_object"}
        )  # type: ignore
        retry = 3
        while retry > 0:
            try:
                result = json.loads(clean_json_response(response))  # type: ignore
                if "selected_option" not in result or "evaluation" not in result:
                    raise ValueError("Invalid guidance selection format")
                if (
                    "attitude" not in result["evaluation"]
                    or "subjective_norm" not in result["evaluation"]
                    or "perceived_control" not in result["evaluation"]
                    or "reasoning" not in result["evaluation"]
                ):
                    raise ValueError(
                        "Evaluation must include attitude, subjective_norm, perceived_control, and reasoning"
                    )
                return result
            except Exception as e:
                logger.warning(f"Error parsing guidance selection response: {str(e)}")
                retry -= 1
        return None

    async def generate_detailed_plan(
        self, selected_option: str
    ) -> Dict:
        """Generate detailed execution plan"""
        position_now = await self.memory.status.get("position")
        home_location = await self.memory.status.get("home")
        work_location = await self.memory.status.get("work")
        current_location = "Out"
        if (
            "aoi_position" in position_now
            and position_now["aoi_position"] == home_location["aoi_position"]
        ):
            current_location = "At home"
        elif (
            "aoi_position" in position_now
            and position_now["aoi_position"] == work_location["aoi_position"]
        ):
            current_location = "At workplace"
        current_time = await self.simulator.get_time(format_time=True)
        self.detail_prompt.format(
            weather=self.simulator.sence("weather"),
            temperature=self.simulator.sence("temperature"),
            selected_option=selected_option,
            current_location=current_location,
            current_time=current_time,
            emotion_types=await self.memory.status.get("emotion_types"),
            thought=await self.memory.status.get("thought"),
            max_plan_steps=self.max_plan_steps,
        )

        response = await self.llm.atext_request(self.detail_prompt.to_dialog())
        retry = 3
        while retry > 0:
            try:
                result = json.loads(clean_json_response(response))  # type: ignore
                if (
                    "plan" not in result
                    or "target" not in result["plan"]
                    or "steps" not in result["plan"]
                ):
                    raise ValueError("Invalid plan format")
                for step in result["plan"]["steps"]:
                    if "intention" not in step or "type" not in step:
                        raise ValueError("Each step must have an intention and a type")
                return result
            except Exception as e:
                logger.warning(f"Error parsing detailed plan: {str(e)}")
                retry -= 1
        return None

    async def forward(self):
        # Step 1: Select guidance plan
        current_need = await self.memory.status.get("current_need")
        guidance_result = await self.select_guidance(current_need)
        if not guidance_result:
            return

        # Step 2: Generate detailed plan
        detailed_plan = await self.generate_detailed_plan(
            guidance_result["selected_option"]
        )

        if not detailed_plan:
            await self.memory.status.update("current_plan", None)
            await self.memory.status.update(
                "current_step", {"intention": "", "type": ""}
            )
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
            "guidance": guidance_result,  # Save the evaluation result of the plan selection
        }
        formated_steps = "\n".join(
            [f"{i}. {step['intention']}" for i, step in enumerate(plan["steps"], 1)]
        )
        formated_plan = f"""
Overall Target: {plan['target']}
Execution Steps: \n{formated_steps}
        """
        plan["start_time"] = await self.simulator.get_time(format_time=True)
        await self.memory.status.update("current_plan", plan)
        await self.memory.status.update(
            "current_step", steps[0] if steps else {"intention": "", "type": ""}
        )
        await self.memory.status.update("execution_context", {"plan": formated_plan})
