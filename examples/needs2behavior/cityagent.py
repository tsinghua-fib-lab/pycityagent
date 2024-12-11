from examples.needs2behavior.blocks.economy_block import EconomyBlock
from examples.needs2behavior.blocks.mobility_block import MobilityBlock
from examples.needs2behavior.blocks.needs_block import NeedsBlock
from examples.needs2behavior.blocks.other import OtherBlock
from examples.needs2behavior.blocks.plan_block import PlanBlock
from examples.needs2behavior.blocks.social_block import SocialBlock
from pycityagent import CitizenAgent, Simulator
from pycityagent.llm.llm import LLM
from pycityagent.memory import Memory
from pycityagent.workflow import GetMap
from pycityagent.workflow.tool import ResetAgentPosition, UpdateWithSimulator


class MyAgent(CitizenAgent):
    update_with_sim = UpdateWithSimulator()
    reset_pos = ResetAgentPosition()

    def __init__(self, name: str, llm_client: LLM, simulator: Simulator | None = None, memory: Memory | None = None) -> None:
        super().__init__(name, llm_client, simulator, memory)
        self.needsBlock = NeedsBlock(llm=self.LLM, memory=self.memory)
        self.planBlock = PlanBlock(llm=self.LLM, memory=self.memory)
        self.mobilityBlock = MobilityBlock(llm=self.LLM, memory=self.memory)
        self.socialBlock = SocialBlock(llm=self.LLM, memory=self.memory)
        self.economyBlock = EconomyBlock(llm=self.LLM, memory=self.memory)
        self.otherBlock = OtherBlock(llm=self.LLM, memory=self.memory)

    # Main workflow
    async def forward(self):
        # 与模拟器同步状态
        await self.update_with_sim()
        # 需求更新
        await self.needsBlock.forward()
        current_need = await self.memory.get("current_need")
        print(f"当前需求: {current_need}")

        # 计划生成
        current_plan = await self.memory.get("current_plan")
        if current_need != "none" and not current_plan:
            await self.planBlock.forward()
        current_plan = await self.memory.get("current_plan")

        # 计划执行
        current_step = await self.memory.get("current_step")
        # 检查 current_step 是否有效（不为空）
        if current_step and current_step.get("type") and current_step.get("intention"):
            step_type = current_step.get("type")
            print(f"执行步骤: {current_step['intention']} - 类型: {step_type}")
            
            if step_type == "mobility":
                result = await self.mobilityBlock.forward(current_step, current_plan)
            elif step_type == "social":
                result = await self.socialBlock.forward(current_step, current_plan)
            elif step_type == "economy":
                result = await self.economyBlock.forward(current_step, current_plan)
            elif step_type == "other":
                result = await self.otherBlock.forward(current_step, current_plan)
            current_step['evaluation'] = result
            
            # 重新查找更新后的 current_step
            current_step_index = next((i for i, step in enumerate(current_plan["steps"]) if step['intention'] == current_step['intention'] and step['type'] == current_step['type']), None)
            current_plan["steps"][current_step_index] = current_step
            await self.memory.update("current_plan", current_plan)
            if current_step_index is not None and current_step_index + 1 < len(current_plan["steps"]):
                next_step = current_plan["steps"][current_step_index + 1]
                await self.memory.update("current_step", next_step)
            else:
                # 标记计划完成
                current_plan["completed"] = True
                await self.memory.update("current_plan", current_plan)
                await self.memory.update("current_step", {"intention": "", "type": ""})
                print("计划执行完毕。\n")