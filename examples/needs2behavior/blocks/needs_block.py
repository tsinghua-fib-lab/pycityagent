import json
from __other import Memory
from pycityagent.llm.llm import LLM
from pycityagent.workflow.block import Block
from pycityagent.workflow.prompt import FormatPrompt


alpha_H, alpha_D = 0.05, 0.04  # 饥饿感与疲劳感自然衰减速率
T_H, T_D = 0.2, 0.2  # 饥饿感与疲劳感临界值
T_P = 0.2  # 安全需求临界值
T_C = 0.2  # 社会需求临界值

EVALUATION_PROMPT = """你是一个智能体的评估系统。智能体为了满足{current_need}需求，执行了以下行为：

目标: {plan_target}
执行步骤:
{evaluation_results}

当前需求状态: {current_needs}

请根据以上执行结果对{current_need}需求的值进行评估和调整。

注意：
1. 需求值范围为0-1，其中：
   - 1表示需求完全满足
   - 0表示需求完全不满足
   - 数值越大表示需求满足度越高
2. 只需要返回{current_need}需求的新值
3. 返回格式如下：
{{
    "{current_need}": 新的需求值
}}

示例：
如果执行结果表明需求得到了较好的满足，可能返回：
{{
    "hungry": 0.8
}}
"""

class NeedsBlock(Block):
    """
    Generate needs
    """
    def __init__(self, llm: LLM, memory: Memory):
        self.llm = llm
        self.memory = memory
        self.evaluation_prompt = FormatPrompt(EVALUATION_PROMPT)

    async def forward(self):
        # 计算时间差并更新需求
        # TODO: 计算时间差
        time_diff = 0.5
        needs = await self.memory.get("needs")
        
        # 根据经过的时间计算饥饿与疲劳的衰减
        hungry_decay = alpha_H * time_diff
        tired_decay = alpha_D * time_diff
        hungry = max(0, needs["hungry"] - hungry_decay)
        tired = max(0, needs["tired"] - tired_decay)
        safe = needs["safe"]
        social = needs["social"]
        needs["hungry"] = hungry
        needs["tired"] = tired

        # TODO: 响应外部事件与消息更新安全需求与社交需求
        await self.memory.update("needs", needs)
        
        print(f"时间流逝: {time_diff:.2f}小时")
        print(f"当前状态 - 饥饿: {hungry:.2f}, 疲劳: {tired:.2f}, 安全: {safe:.2f}, 社交: {social:.2f}")
                
        # 判断当前是否有正在执行的plan
        current_plan = await self.memory.get("current_plan")
        if current_plan and current_plan.get("completed"):
            # 评估计划执行过程并调整需求
            await self.evaluate_and_adjust_needs(current_plan)
            # 将完成的计划添加到历史记录
            history = await self.memory.get("plan_history")
            history.append(current_plan)
            await self.memory.update("plan_history", history)
            await self.memory.update("current_plan", None)

        # 如果需要调整需求，更新当前需求
        # 调整方案为，如果当前的需求为空，或有更高级的需求出现，则调整需求
        current_need = await self.memory.get("current_need")
        
        # 当前没有计划或计划已执行完毕，获取所有需求值，按优先级检查各需求是否达到阈值
        if not current_plan or current_plan.get("completed"):
            # 按优先级顺序检查需求
            if hungry <= T_H:
                await self.memory.update("current_need", "hungry")
                print("需求调整为：饥饿")
            elif tired <= T_D:
                await self.memory.update("current_need", "tired") 
                print("需求调整为：疲劳")
            elif safe <= T_P:
                await self.memory.update("current_need", "safe")
                print("需求调整为：安全需求")
            elif social <= T_C:
                await self.memory.update("current_need", "social")
                print("需求调整为：社交需求")
            else:
                await self.memory.update("current_need", "none")
                print("当前无需求。")
        else:
            # 有正在执行的计划时,只在出现更高优先级需求时调整
            needs_changed = False
            if hungry <= T_H and current_need not in ["hungry", "tired"]:
                await self.memory.update("current_need", "hungry")
                print("出现更高优先级需求,调整为：饥饿")
                needs_changed = True
            elif tired <= T_D and current_need not in ["hungry", "tired"]:
                await self.memory.update("current_need", "tired")
                print("出现更高优先级需求,调整为：疲劳")
                needs_changed = True
            elif safe <= T_P and current_need not in ["hungry", "tired", "safe"]:
                await self.memory.update("current_need", "safe")
                print("出现更高优先级需求,调整为：安全需求")
                needs_changed = True
            elif social <= T_C and current_need not in ["hungry", "tired", "safe", "social"]:
                await self.memory.update("current_need", "social")
                print("出现更高优先级需求,调整为：社交需求")
                needs_changed = True
                
            # 如果需求发生变化,中断当前计划
            if needs_changed:
                await self.memory.update("current_plan", None)
                await self.memory.update("current_step", {"intention": "", "type": ""})
                print("由于需求变化,当前计划已中断")

    async def evaluate_and_adjust_needs(self, completed_plan):
        # 获取执行的计划和评估结果
        evaluation_results = []
        for step in completed_plan["steps"]:
            evaluation_results.append(f"- {step['intention']} ({step['type']}): {step['evaluation']['evaluation']}")
        evaluation_results = "\n".join(evaluation_results)

        # 使用 LLM 进行评估
        current_need = await self.memory.get("current_need")
        self.evaluation_prompt.format(
            current_need=current_need,
            plan_target=completed_plan["target"],
            evaluation_results=evaluation_results,
            current_needs=await self.memory.get("needs")
        )

        response = await self.llm.atext_request(
            self.evaluation_prompt.to_dialog()
        )

        try:
            print("\n=== 需求评估 ===")
            print(f"评估需求: {current_need}")
            print(f"执行计划: {completed_plan['target']}")
            print("执行结果:")
            print(evaluation_results)
            
            new_needs = json.loads(response)
            # 更新所有需求的数值
            needs = await self.memory.get("needs")
            print(f"\n需求值调整:")
            for need_type, new_value in new_needs.items():
                if need_type in needs:
                    old_value = needs[need_type]
                    needs[need_type] = new_value
                    print(f"- {need_type}: {old_value} -> {new_value}")
            await self.memory.update("needs", needs)
            print("===============\n")
        except json.JSONDecodeError:
            print(f"评估响应不是有效的JSON格式: {response}")
        except Exception as e:
            print(f"处理评估响应时发生错误: {str(e)}")
            print(f"原始响应: {response}")