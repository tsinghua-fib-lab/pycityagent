import asyncio
from datetime import datetime, timedelta
from examples.cityagent.blocks.cognition_block import CognitionBlock
from examples.cityagent.blocks.economy_block import EconomyBlock
from examples.cityagent.blocks.mobility_block import MobilityBlock
from examples.cityagent.blocks.needs_block import NeedsBlock
from examples.cityagent.blocks.other import OtherBlock
from examples.cityagent.blocks.plan_block import PlanBlock
from examples.cityagent.blocks.social_block import SocialBlock
from pycityagent import CitizenAgent, Simulator
from pycityagent.llm.llm import LLM
from pycityagent.memory import Memory
from pycityagent.workflow.tool import ResetAgentPosition, UpdateWithSimulator


class MyAgent(CitizenAgent):
    update_with_sim = UpdateWithSimulator()
    reset_pos = ResetAgentPosition()

    def __init__(self, name: str, llm_client: LLM, simulator: Simulator | None = None, memory: Memory | None = None) -> None:
        super().__init__(name, llm_client, simulator, memory)
        self.needsBlock = NeedsBlock(llm=self.LLM, memory=self.memory)
        self.planBlock = PlanBlock(llm=self.LLM, memory=self.memory)
        self.mobilityBlock = MobilityBlock(llm=self.LLM, memory=self.memory, simulator=simulator) # type: ignore
        self.socialBlock = SocialBlock(llm=self.LLM, memory=self.memory)
        self.economyBlock = EconomyBlock(llm=self.LLM, memory=self.memory)
        self.cognitionBlock = CognitionBlock(llm=self.LLM, memory=self.memory)
        self.otherBlock = OtherBlock(llm=self.LLM, memory=self.memory)

    # Main workflow
    async def forward(self):
        # 认知更新
        await self.cognitionBlock.forward()

        # 与模拟器同步智能体的状态
        await self.update_with_sim()
        # 获取当前状态
        MOTION_KEYS = {
            "status",
            "position",
            "v",
        }
        res_dict = {}
        for _key in MOTION_KEYS:
            try:
                res_dict[_key] = await self.memory.get(_key)
            except:
                pass
        agent_id = await self.memory.get("id")
        print(f"Status of Agent {agent_id}:{res_dict}")
        if res_dict['status'] == 2:
            # 正在运动
            print("智能体正在移动中")
            await asyncio.sleep(1)
            return

        # 需求更新
        time_now = await self.simulator.GetTime(format_time=True)
        print(f"Current time: {time_now}")
        await self.needsBlock.forward(time_now=time_now)
        current_need = await self.memory.get("current_need")
        print(f"当前需求: {current_need}")

        # 计划生成
        current_plan = await self.memory.get("current_plan")
        if current_need != "none" and not current_plan:
            await self.planBlock.forward()
        current_plan = await self.memory.get("current_plan")
        execution_context = await self.memory.get("execution_context")

        # 计划执行
        current_step = await self.memory.get("current_step")
        # 检查 current_step 是否有效（不为空）
        if current_step and current_step.get("type") and current_step.get("intention"):
            step_type = current_step.get("type")
            print(f"执行步骤: {current_step['intention']} - 类型: {step_type}")
            time_start_exec = str(await self.simulator.GetTime(format_time=True))
            time_start_exec = datetime.strptime(time_start_exec, "%H:%M:%S")
            result = None
            if step_type == "mobility":
                result = await self.mobilityBlock.forward(current_step, execution_context)
            elif step_type == "social":
                result = await self.socialBlock.forward(current_step, execution_context)
            elif step_type == "economy":
                result = await self.economyBlock.forward(current_step, execution_context)
            elif step_type == "other":
                result = await self.otherBlock.forward(current_step, execution_context)
            if result != None:
                print(f"执行结果: {result}")
                time_end_exec_actual = str(await self.simulator.GetTime(format_time=True))
                time_end_exec_actual = datetime.strptime(time_end_exec_actual, "%H:%M:%S")
                time_end_plan = time_start_exec + timedelta(minutes=result['consumed_time'])
                if time_end_plan >= time_end_exec_actual:
                    # 等待
                    while time_end_plan >= time_end_exec_actual:
                        await asyncio.sleep(1)
                        time_end_exec_actual = str(await self.simulator.GetTime(format_time=True))
                        time_end_exec_actual = datetime.strptime(time_end_exec_actual, "%H:%M:%S")
                else:
                    # 取两者大者
                    result['consumed_time'] = int((time_end_plan - time_start_exec).total_seconds()/60)

                # 更新当前步骤的评估结果
                current_step['evaluation'] = result
            
            # 重新查找更新后的 current_step
            current_step_index = next((i for i, step in enumerate(current_plan["steps"]) if step['intention'] == current_step['intention'] and step['type'] == current_step['type']), None)
            current_plan["steps"][current_step_index] = current_step
            await self.memory.update("current_plan", current_plan)
            await self.memory.update("execution_context", execution_context)
            if current_step_index is not None and current_step_index + 1 < len(current_plan["steps"]):
                next_step = current_plan["steps"][current_step_index + 1]
                await self.memory.update("current_step", next_step)
            else:
                # 标记计划完成
                current_plan["completed"] = True
                await self.memory.update("current_plan", current_plan)
                await self.memory.update("current_step", {"intention": "", "type": ""})
                print("计划执行完毕。\n")