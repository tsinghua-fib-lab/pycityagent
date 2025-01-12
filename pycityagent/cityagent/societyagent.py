import asyncio
import json
import logging
from typing import Optional

from pycityagent import CitizenAgent, Simulator
from pycityagent.agent import Agent
from pycityagent.economy import EconomyClient
from pycityagent.llm.llm import LLM
from pycityagent.memory import Memory
from pycityagent.message import Messager
from pycityagent.workflow import Block
from pycityagent.tools import UpdateWithSimulator

from .blocks import (CognitionBlock, EconomyBlock, MobilityBlock, NeedsBlock,
                     OtherBlock, PlanBlock, SocialBlock)
from .blocks.economy_block import MonthPlanBlock

logger = logging.getLogger("pycityagent")


class PlanAndActionBlock(Block):
    """主动工作流"""

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
    ):
        super().__init__(
            name="plan_and_action_block", llm=llm, memory=memory, simulator=simulator
        )
        self._agent = agent
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

    async def check_and_update_step(self):
        status = await self.memory.get("status")
        if status == 2:
            # 正在运动
            logger.info("Agent is moving")
            await asyncio.sleep(1)
            return False

        # 获取上一步信息
        current_step = await self.memory.get("current_step")
        if current_step["intention"] == "" or current_step["type"] == "":
            # 没有上一步，直接返回
            return True
        time_now = int(await self.simulator.get_time())
        step_start_time = current_step["start_time"]
        step_consumed_time = current_step["evaluation"]["consumed_time"]
        time_end_plan = step_start_time + int(step_consumed_time) * 60
        if time_now >= time_end_plan:
            # 上一步执行完成
            current_plan = await self.memory.get("current_plan")
            current_step["evaluation"]["consumed_time"] = (
                time_now - step_start_time
            ) / 60
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
            await self.memory.update("current_plan", current_plan)
            if current_step_index is not None and current_step_index + 1 < len(
                current_plan["steps"]
            ):
                next_step = current_plan["steps"][current_step_index + 1]
                await self.memory.update("current_step", next_step)
            else:
                # 标记计划完成
                current_plan["completed"] = True
                current_plan["end_time"] = await self.simulator.get_time(
                    format_time=True
                )
                await self.memory.update("current_plan", current_plan)
                await self.memory.update("current_step", {"intention": "", "type": ""})
                logger.info("Current plan execution completed.\n")
            return True
        # 上一步未执行完成
        return False

    async def forward(self):
        # 与模拟器同步智能体的状态
        await self._agent.update_with_sim()
        # 检测上一步是否执行完成
        if not await self.check_and_update_step():
            return

        # 长期决策
        await self.longTermDecisionBlock.forward()

        # 需求更新
        time_now = await self.simulator.get_time(format_time=True)
        logger.info(f"Current time: {time_now}")
        await self.needsBlock.forward()
        current_need = await self.memory.get("current_need")
        logger.info(f"Current need: {current_need}")

        # 计划生成
        current_plan = await self.memory.get("current_plan")
        if current_need != "none" and not current_plan:
            await self.planBlock.forward()
        current_plan = await self.memory.get("current_plan")
        execution_context = await self.memory.get("execution_context")
        current_step = await self.memory.get("current_step")
        # 检查 current_step 是否有效（不为空）
        if current_step and current_step.get("type") and current_step.get("intention"):
            step_type = current_step.get("type")
            position = await self.memory.get("position")
            if "aoi_position" in position:
                current_step["position"] = position["aoi_position"]["aoi_id"]
            current_step["start_time"] = int(await self.simulator.get_time())
            logger.info(
                f"Executing step: {current_step['intention']} - Type: {step_type}"
            )
            result = None
            if step_type == "mobility":
                result = await self.mobilityBlock.forward(
                    current_step, execution_context
                )
            elif step_type == "social":
                result = await self.socialBlock.forward(current_step, execution_context)
            elif step_type == "economy":
                result = await self.economyBlock.forward(
                    current_step, execution_context
                )
            elif step_type == "other":
                result = await self.otherBlock.forward(current_step, execution_context)
            if result != None:
                logger.info(f"Execution result: {result}")
                current_step["evaluation"] = result

            # 更新current_step信息，plan信息以及execution_context信息
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
            await self.memory.update("current_step", current_step)
            await self.memory.update("current_plan", current_plan)
            await self.memory.update("execution_context", execution_context)


class MindBlock(Block):
    """认知工作流"""

    cognitionBlock: CognitionBlock

    def __init__(self, llm: LLM, memory: Memory, simulator: Simulator):
        super().__init__(name="mind_block", llm=llm, memory=memory, simulator=simulator)
        self.cognitionBlock = CognitionBlock(
            llm=llm, memory=memory, simulator=simulator
        )

    async def forward(self):
        await self.cognitionBlock.forward()


class SocietyAgent(CitizenAgent):
    mindBlock: MindBlock
    planAndActionBlock: PlanAndActionBlock
    update_with_sim = UpdateWithSimulator()

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
        self.mindBlock = MindBlock(
            llm=self._llm_client, memory=self._memory, simulator=self._simulator
        )
        self.planAndActionBlock = PlanAndActionBlock(
            agent=self,
            llm=self._llm_client,
            memory=self._memory,
            simulator=self._simulator,
            economy_client=self._economy_client,
        )
        self.step_count = -1

    # Main workflow
    async def forward(self):
        logger.info(f"Agent {self._uuid} forward")
        self.step_count += 1
        # 多工作流并发执行
        task_list = [
            asyncio.create_task(self.mindBlock.forward()),
            asyncio.create_task(self.planAndActionBlock.forward()),
        ]
        await asyncio.gather(*task_list)

    async def process_agent_chat_response(self, payload: dict) -> str:
        if payload["type"] == "social":
            resp = f"Agent {self._uuid} received agent chat response: {payload}"
            logger.info(resp)
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

                # Get chat histories and ensure proper format
                chat_histories = await self._memory.get("chat_histories") or {}
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
                    await self._memory.update("chat_histories", chat_histories)
                    logger.info(
                        f"Message propagation limit reached ({propagation_count} > 5), stopping propagation"
                    )
                    return ""

                # Get relationship score
                relationships = await self._memory.get("relationships") or {}
                relationship_score = relationships.get(sender_id, 50)

                # Decision prompt
                should_respond_prompt = f"""Based on:
        - Received message: "{content}"
        - Our relationship score: {relationship_score}/100
        - My profile: {{
            "gender": "{await self._memory.get("gender") or ""}",
            "education": "{await self._memory.get("education") or ""}",
            "personality": "{await self._memory.get("personality") or ""}",
            "occupation": "{await self._memory.get("occupation") or ""}"
        }}
        - Recent chat history: {chat_histories.get(sender_id, "")}

        Should I respond to this message? Consider:
        1. Is this a message that needs/deserves a response?
        2. Would it be natural for someone with my personality to respond?
        3. Is our relationship close enough to warrant a response?

        Answer only YES or NO."""

                should_respond = await self._llm_client.atext_request(
                    [
                        {
                            "role": "system",
                            "content": "You are helping decide whether to respond to a message.",
                        },
                        {"role": "user", "content": should_respond_prompt},
                    ]
                )

                if should_respond.strip().upper() != "YES":
                    await self._memory.update("chat_histories", chat_histories)
                    return ""

                response_prompt = f"""Based on:
        - Received message: "{content}"
        - Our relationship score: {relationship_score}/100
        - My profile: {{
            "gender": "{await self._memory.get("gender") or ""}",
            "education": "{await self._memory.get("education") or ""}",
            "personality": "{await self._memory.get("personality") or ""}",
            "occupation": "{await self._memory.get("occupation") or ""}"
        }}
        - Recent chat history: {chat_histories.get(sender_id, "")}

        Generate an appropriate response that:
        1. Matches my personality and background
        2. Maintains natural conversation flow
        3. Is concise (under 100 characters)
        4. Reflects our relationship level

        Response should be ONLY the message text, no explanations."""

                response = await self._llm_client.atext_request(
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
                    await self._memory.update("chat_histories", chat_histories)

                    # Send response
                    serialized_response = json.dumps(
                        {
                            "content": response,
                            "propagation_count": propagation_count + 1,
                        },
                        ensure_ascii=False,
                    )
                    await self.send_message_to_agent(sender_id, serialized_response)
                    logger.info("sender_id", sender_id)
                    logger.info("message", serialized_response)
                return response

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
            await self.memory.update(key, value)
