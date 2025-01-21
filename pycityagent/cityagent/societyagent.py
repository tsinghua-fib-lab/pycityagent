import asyncio
import json
import logging
from typing import Optional

from pycityagent import CitizenAgent, Simulator
from pycityagent.agent import Agent
from pycityagent.economy import EconomyClient
from pycityagent.llm.llm import LLM
from pycityagent.memory import Memory
from pycityagent.tools import UpdateWithSimulator
from pycityagent.workflow import Block

from .blocks import (CognitionBlock, EconomyBlock, MobilityBlock, NeedsBlock,
                     OtherBlock, PlanBlock, SocialBlock)
from .blocks.economy_block import MonthPlanBlock

logger = logging.getLogger("pycityagent")


class PlanAndActionBlock(Block):
    """Active workflow based on needs model and plan behavior model"""

    longTermDecisionBlock: MonthPlanBlock
    needsBlock: NeedsBlock
    planBlock: PlanBlock
    mobilityBlock: MobilityBlock
    socialBlock: SocialBlock
    economyBlock: EconomyBlock
    otherBlock: OtherBlock

    def __init__(
        self,
        agent: Agent,
        llm: LLM,
        memory: Memory,
        simulator: Simulator,
        economy_client: EconomyClient,
        enable_mobility: bool = True,
        enable_social: bool = True,
        enable_economy: bool = True,
        enable_cognition: bool = True,
    ):
        super().__init__(
            name="plan_and_action_block", llm=llm, memory=memory, simulator=simulator
        )
        self._agent = agent
        self.enable_mobility = enable_mobility
        self.enable_social = enable_social
        self.enable_economy = enable_economy
        self.enable_cognition = enable_cognition
        self.longTermDecisionBlock = MonthPlanBlock(
            llm=llm, memory=memory, simulator=simulator, economy_client=economy_client
        )
        self.needsBlock = NeedsBlock(llm=llm, memory=memory, simulator=simulator)
        self.planBlock = PlanBlock(llm=llm, memory=memory, simulator=simulator)
        self.mobilityBlock = MobilityBlock(llm=llm, memory=memory, simulator=simulator)
        self.socialBlock = SocialBlock(
            agent=self, llm=llm, memory=memory, simulator=simulator
        )
        self.economyBlock = EconomyBlock(
            llm=llm, memory=memory, simulator=simulator, economy_client=economy_client
        )
        self.otherBlock = OtherBlock(llm=llm, memory=memory)
    async def plan_generation(self):
        """Generate plan"""
        current_plan = await self.memory.status.get("current_plan")
        current_need = await self.memory.status.get("current_need")
        if current_need != "none" and not current_plan:
            await self.planBlock.forward()

    async def step_execution(self):
        """Execute the current step"""
        current_plan = await self.memory.status.get("current_plan")
        execution_context = await self.memory.status.get("execution_context")
        current_step = await self.memory.status.get("current_step")
        # check current_step is valid (not empty)
        if current_step and current_step.get("type") and current_step.get("intention"):
            step_type = current_step.get("type")
            position = await self.memory.status.get("position")
            if "aoi_position" in position:
                current_step["position"] = position["aoi_position"]["aoi_id"]
            current_step["start_time"] = int(await self.simulator.get_time())
            result = None
            if step_type == "mobility":
                if self.enable_mobility:  # type:ignore
                    result = await self.mobilityBlock.forward(
                        current_step, execution_context
                    )
                else:
                    result = {
                        "success": False,
                        "evaluation": f"Mobility Behavior is disabled",
                        "consumed_time": 0,
                        "node_id": None,
                    }
            elif step_type == "social":
                if self.enable_social:  # type:ignore
                    result = await self.socialBlock.forward(
                        current_step, execution_context
                    )
                else:
                    result = {
                        "success": False,
                        "evaluation": f"Social Behavior is disabled",
                        "consumed_time": 0,
                        "node_id": None,
                    }
            elif step_type == "economy":
                if self.enable_economy:  # type:ignore
                    result = await self.economyBlock.forward(
                        current_step, execution_context
                    )
                else:
                    result = {
                        "success": False,
                        "evaluation": f"Economy Behavior is disabled",
                        "consumed_time": 0,
                        "node_id": None,
                    }
            elif step_type == "other":
                result = await self.otherBlock.forward(current_step, execution_context)
            if result != None:
                current_step["evaluation"] = result

            # Update current_step, plan, and execution_context information
            current_step_index = next(
                (
                    i
                    for i, step in enumerate(current_plan["steps"])
                    if step["intention"] == current_step["intention"]
                    and step["type"] == current_step["type"]
                ),
                None,
            )
            current_plan["steps"][current_step_index] = current_step
            await self.memory.status.update("current_step", current_step)
            await self.memory.status.update("current_plan", current_plan)
            await self.memory.status.update("execution_context", execution_context)

    async def forward(self):
        # Long-term decision
        await self.longTermDecisionBlock.forward()

        # update needs
        await self.needsBlock.forward()

        # plan generation
        await self.plan_generation()

        # step execution
        await self.step_execution()

class MindBlock(Block):
    """Cognition workflow"""
    cognitionBlock: CognitionBlock

    def __init__(self, llm: LLM, memory: Memory, simulator: Simulator):
        super().__init__(name="mind_block", llm=llm, memory=memory, simulator=simulator)
        self.cognitionBlock = CognitionBlock(
            llm=self.llm, memory=self.memory, simulator=simulator
        )

    async def forward(self):
        await self.cognitionBlock.forward()

class SocietyAgent(CitizenAgent):
    update_with_sim = UpdateWithSimulator()
    mindBlock: MindBlock
    planAndActionBlock: PlanAndActionBlock
    update_with_sim = UpdateWithSimulator()
    configurable_fields = [
        "enable_cognition",
        "enable_mobility",
        "enable_social",
        "enable_economy",
    ]
    default_values = {
        "enable_cognition": True,
        "enable_mobility": True,
        "enable_social": True,
        "enable_economy": True,
    }
    fields_description = {
        "enable_cognition": "Enable cognition workflow",
        "enable_mobility": "Enable mobility workflow",
        "enable_social": "Enable social workflow",
        "enable_economy": "Enable economy workflow",
    }

    def __init__(
        self,
        name: str,
        llm_client: Optional[LLM] = None,
        simulator: Optional[Simulator] = None,
        memory: Optional[Memory] = None,
        economy_client: Optional[EconomyClient] = None,
    ) -> None:
        super().__init__(
            name=name,
            llm_client=llm_client,
            simulator=simulator,
            memory=memory,
            economy_client=economy_client,
        )

        # config
        self.enable_cognition = True
        self.enable_mobility = True
        self.enable_social = True
        self.enable_economy = True

        self.mindBlock = MindBlock(
            llm=self.llm, memory=self.memory, simulator=self.simulator
        )
        self.planAndActionBlock = PlanAndActionBlock(
            agent=self,
            llm=self.llm,
            memory=self.memory,
            simulator=self.simulator,
            economy_client=self.economy_client,
            enable_mobility=self.enable_mobility,
            enable_social=self.enable_social,
            enable_economy=self.enable_economy,
            enable_cognition=self.enable_cognition,
        )
        self.step_count = -1
        self.cognition_update = -1

    # Main workflow
    async def forward(self):
        self.step_count += 1
        # sync agent status with simulator
        await self.update_with_sim()

        # check last step
        ifpass = await self.check_and_update_step()
        if not ifpass:
            return
        
        await self.planAndActionBlock.forward()

        if self.enable_cognition:
            await self.mindBlock.forward()

    async def check_and_update_step(self):
        """Check if the previous step has been completed"""
        status = await self.memory.status.get("status")
        if status == 2:
            # Agent is moving
            await asyncio.sleep(1)
            return False

        # Get the previous step information
        current_step = await self.memory.status.get("current_step")
        if current_step["intention"] == "" or current_step["type"] == "":
            # No previous step, return directly
            return True
        time_now = int(await self.simulator.get_time())
        step_start_time = current_step["start_time"]
        step_consumed_time = current_step["evaluation"]["consumed_time"]
        time_end_plan = step_start_time + int(step_consumed_time) * 60
        if time_now >= time_end_plan:
            # The previous step has been completed
            current_plan = await self.memory.status.get("current_plan")
            current_step["evaluation"]["consumed_time"] = (
                time_now - step_start_time
            ) / 60
            current_plan["stream_nodes"].append(current_step["evaluation"]["node_id"])
            if current_step["evaluation"]["success"]:
                # Last step is completed
                current_step_index = next(
                    (
                        i
                        for i, step in enumerate(current_plan["steps"])
                        if step["intention"] == current_step["intention"]
                        and step["type"] == current_step["type"]
                    ),
                    None,
                )
                current_plan["steps"][current_step_index] = current_step
                await self.memory.status.update("current_plan", current_plan)
                if current_step_index is not None and current_step_index + 1 < len(
                    current_plan["steps"]
                ):
                    next_step = current_plan["steps"][current_step_index + 1]
                    await self.memory.status.update("current_step", next_step)
                else:
                    # Whole plan is completed
                    current_plan["completed"] = True
                    current_plan["end_time"] = await self.simulator.get_time(
                        format_time=True
                    )
                    if self.enable_cognition:
                        # Update emotion for the plan
                        related_memories = await self.memory.stream.get_by_ids(
                            current_plan["stream_nodes"]
                        )
                        incident = f"You have successfully completed the plan: {related_memories}"
                        conclusion = await self.mindBlock.cognitionBlock.emotion_update(
                            incident
                        )
                        await self.memory.stream.add_cognition(
                            description=conclusion  # type:ignore
                        )
                        await self.memory.stream.add_cognition_to_memory(
                            current_plan["stream_nodes"], conclusion  # type:ignore
                        )
                    await self.memory.status.update("current_plan", current_plan)
                    await self.memory.status.update(
                        "current_step", {"intention": "", "type": ""}
                    )
                return True
            else:
                current_plan["failed"] = True
                current_plan["end_time"] = await self.simulator.get_time(
                    format_time=True
                )
                if self.enable_cognition:
                    # Update emotion for the plan
                    related_memories = await self.memory.stream.get_by_ids(
                        current_plan["stream_nodes"]
                    )
                    incident = (
                        f"You have failed to complete the plan: {related_memories}"
                    )
                    conclusion = await self.mindBlock.cognitionBlock.emotion_update(
                        incident
                    )
                    await self.memory.stream.add_cognition(
                        description=conclusion  # type:ignore
                    )
                    await self.memory.stream.add_cognition_to_memory(
                        current_plan["stream_nodes"], conclusion  # type:ignore
                    )
                await self.memory.status.update("current_plan", current_plan)
                await self.memory.status.update(
                    "current_step", {"intention": "", "type": ""}
                )
        # The previous step has not been completed
        return False

    async def process_agent_chat_response(self, payload: dict) -> str:  # type:ignore
        if payload["type"] == "social":
            resp = f"Agent {self._uuid} received agent chat response: {payload}"
            try:
                # Extract basic info
                sender_id = payload.get("from")
                if not sender_id:
                    return ""

                raw_content = payload.get("content", "")

                # Parse message content
                try:
                    message_data = json.loads(raw_content)
                    content = message_data["content"]
                    propagation_count = message_data.get("propagation_count", 1)
                except (json.JSONDecodeError, TypeError, KeyError):
                    content = raw_content
                    propagation_count = 1

                if not content:
                    return ""
                
                # 添加记忆
                description = f"You received a social message: {content}"
                await self.memory.stream.add_social(description=description)
                if self.enable_cognition:
                    # 更新情绪
                    await self.mindBlock.cognitionBlock.emotion_update(description)

                # Get chat histories and ensure proper format
                chat_histories = await self.memory.status.get("chat_histories") or {}
                if not isinstance(chat_histories, dict):
                    chat_histories = {}

                # Update chat history with received message
                if sender_id not in chat_histories:
                    chat_histories[sender_id] = ""
                if chat_histories[sender_id]:
                    chat_histories[sender_id] += "，"
                chat_histories[sender_id] += f"them: {content}"

                # Check propagation limit
                if propagation_count > 5:
                    await self.memory.status.update("chat_histories", chat_histories)
                    return ""

                # Get relationship score
                relationships = await self.memory.status.get("relationships") or {}
                relationship_score = relationships.get(sender_id, 50)

                # Decision prompt
                should_respond_prompt = f"""Based on:
        - Received message: "{content}"
        - Our relationship score: {relationship_score}/100
        - My profile: {{
            "gender": "{await self.memory.status.get("gender") or ""}",
            "education": "{await self.memory.status.get("education") or ""}",
            "personality": "{await self.memory.status.get("personality") or ""}",
            "occupation": "{await self.memory.status.get("occupation") or ""}"
        }}
        - My current emotion: {await self.memory.status.get("emotion_types")}
        - Recent chat history: {chat_histories.get(sender_id, "")}

        Should I respond to this message? Consider:
        1. Is this a message that needs/deserves a response?
        2. Would it be natural for someone with my personality to respond?
        3. Is our relationship close enough to warrant a response?

        Answer only YES or NO."""

                should_respond = await self._llm_client.atext_request(  # type:ignore
                    [
                        {
                            "role": "system",
                            "content": "You are helping decide whether to respond to a message.",
                        },
                        {"role": "user", "content": should_respond_prompt},
                    ]
                )

                if should_respond.strip().upper() != "YES":  # type:ignore
                    await self.memory.status.update("chat_histories", chat_histories)
                    return ""

                response_prompt = f"""Based on:
        - Received message: "{content}"
        - Our relationship score: {relationship_score}/100
        - My profile: {{
            "gender": "{await self.memory.status.get("gender") or ""}",
            "education": "{await self.memory.status.get("education") or ""}",
            "personality": "{await self.memory.status.get("personality") or ""}",
            "occupation": "{await self.memory.status.get("occupation") or ""}"
        }}
        - My current emotion: {await self.memory.status.get("emotion_types")}
        - Recent chat history: {chat_histories.get(sender_id, "")}

        Generate an appropriate response that:
        1. Matches my personality and background
        2. Maintains natural conversation flow
        3. Is concise (under 100 characters)
        4. Reflects our relationship level

        Response should be ONLY the message text, no explanations."""

                response = await self.llm.atext_request(
                    [
                        {
                            "role": "system",
                            "content": "You are helping generate a chat response.",
                        },
                        {"role": "user", "content": response_prompt},
                    ]
                )

                if response:
                    # Update chat history with response
                    chat_histories[sender_id] += f"，me: {response}"
                    await self.memory.status.update("chat_histories", chat_histories)

                    # Send response
                    serialized_response = json.dumps(
                        {
                            "content": response,
                            "propagation_count": propagation_count + 1,
                        },
                        ensure_ascii=False,
                    )
                    await self.send_message_to_agent(sender_id, serialized_response)
                return response  # type:ignore

            except Exception as e:
                logger.warning(f"Error in process_agent_chat_response: {str(e)}")
                return ""
        else:
            content = payload["content"]
            key, value = content.split("@")
            if "." in value:
                value = float(value)
            else:
                value = int(value)
            description = f"You received a economic message: Your {key} has changed from {await self.memory.status.get(key)} to {value}"
            await self.memory.status.update(key, value)
            await self.memory.stream.add_economic(  # type:ignore
                description=description
            )
            if self.enable_cognition:
                await self.mindBlock.cognitionBlock.emotion_update(description)
