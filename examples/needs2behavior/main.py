import asyncio
import random

import numpy as np
import yaml

from examples.needs2behavior.blocks.economy_block import EconomyBlock
from examples.needs2behavior.blocks.mobility_block import MobilityBlock
from examples.needs2behavior.blocks.needs_block import NeedsBlock
from examples.needs2behavior.blocks.other import OtherBlock
from examples.needs2behavior.blocks.plan_block import PlanBlock
from examples.needs2behavior.blocks.social_block import SocialBlock
from examples.needs2behavior.utils import choiceHW
from pycityagent import CitizenAgent, Simulator
from pycityagent.llm import LLM, LLMConfig
from pycityagent.memory import Memory
from pycityagent.workflow import GetMap
from examples.needs2behavior.time_utils import TimeManager


class MyAgent(CitizenAgent):
    get_map = GetMap()

    def __init__(self, name: str, llm_client: LLM, simulator: Simulator | None = None, memory: Memory | None = None) -> None:
        super().__init__(name, llm_client, simulator, memory)
        self.needsBlock = NeedsBlock(llm=self.LLM, memory=self.memory)
        self.planBlock = PlanBlock(llm=self.LLM, memory=self.memory)
        self.mobilityBlock = MobilityBlock(llm=self.LLM)
        self.socialBlock = SocialBlock(llm=self.LLM)
        self.economyBlock = EconomyBlock(llm=self.LLM)
        self.otherBlock = OtherBlock(llm=self.LLM)

    # Main workflow
    async def forward(self):
        time_manager = TimeManager()
        print(f"\n=== 当前时间: {time_manager.get_time()} ===")
        await self.needsBlock.forward()
        
        current_need = await self.memory.get("current_need")
        current_plan = await self.memory.get("current_plan")
        current_step = await self.memory.get("current_step")

        print(f"当前需求: {current_need}")
        
        if current_need != "none" and not current_plan:
            await self.planBlock.forward()
        
        # 检查 current_step 是否有效（不为空）
        if current_step and current_step.get("type") and current_step.get("intention"):
            step_type = current_step.get("type")
            print(f"执行步骤: {current_step['intention']} - 类型: {step_type}")
            
            # 随机生成步骤执行时间（10-60分钟）
            step_duration = random.randint(10, 60)
            time_manager.add_minutes(step_duration)
            print(f"步骤耗时: {step_duration}分钟")
            
            if step_type == "mobility":
                await self.mobilityBlock.forward(current_step)
            elif step_type == "social":
                await self.socialBlock.forward(current_step)
            elif step_type == "economy":
                await self.economyBlock.forward(current_step)
            elif step_type == "other":
                await self.otherBlock.forward(current_step)
            
            # 重新查找更新后的 current_step
            current_step_index = next((i for i, step in enumerate(current_plan["steps"]) if step['intention'] == current_step['intention'] and step['type'] == current_step['type']), None)
            if current_step_index is not None and current_step_index + 1 < len(current_plan["steps"]):
                next_step = current_plan["steps"][current_step_index + 1]
                await self.memory.update("current_step", next_step)
                print(f"下一步: {next_step['intention']} - 类型: {next_step['type']}")
            else:
                # 标记计划完成
                current_plan["completed"] = True
                await self.memory.update("current_plan", current_plan)
                await self.memory.update("current_step", {"intention": "", "type": ""})
                print("计划执行完毕。\n")


async def main():
    print("-----Loading configs...")
    with open("__config_template.yaml", "r") as file:
        config = yaml.safe_load(file)

    # Step:1 prepare LLM client
    print("-----Loading LLM client...")
    llmConfig = LLMConfig(config["llm_request"])
    llm = LLM(llmConfig)

    # Step:2 prepare Simulator
    print("-----Loading Simulator...")
    # simulator = Simulator(config["simulator_request"])

    # Step:3 prepare Memory
    print("-----Setting Memory...")
    (home, work) = choiceHW()
    Homeplace = (home[0], home[1])
    Workplace = (work[0], work[1])
    EXTRA_ATTRIBUTES = {
        "needs": (dict, {'hungry': 0.8, # 饥饿感
                         'tired': 0.5, # 疲劳感
                         'safe': 0.3, # 安全需
                         'social': 0.2, # 社会需求
                         }, True),
        "current_need": (str, "none", True),  # 当前需求
        "current_plan": (list, [], True),  # 存储完整的计划步，每个步骤包含执行情况
        "current_step": (dict, {"intention": "", "type": ""}, True),  # 存储当前执行的步骤
        "nowPlace": (tuple, Homeplace, True),
        "home": (tuple, Homeplace, True),
        "work": (tuple, Workplace, True),
        "execution_evaluation": (dict, {"status": "", "details": ""}, True),  # 存储执行情况的评价
        "history": (list, [], True),  # 存储所有的计划历史
    }
    memory = Memory(
        config=EXTRA_ATTRIBUTES,
        profile={
            "gender": "male",
            "education": "Doctor",
            "consumption": "sightly low",
            "occupation": "Student",
        },
    )

    # Step:4 prepare Agent
    my_agent = MyAgent(
        name="MyAgent", llm_client=llm, simulator=None, memory=memory
    )
    for i in range(20):
        await my_agent.forward()


if __name__ == "__main__":
    asyncio.run(main())
