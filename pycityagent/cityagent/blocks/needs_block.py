import json
from pycityagent import Simulator
from pycityagent.memory.memory import Memory
from pycityagent.llm.llm import LLM
from pycityagent.workflow.block import Block
from pycityagent.workflow.prompt import FormatPrompt
import logging
logger = logging.getLogger("pycityagent")

INITIAL_NEEDS_PROMPT = """You are an intelligent agent needs initialization system. Based on the profile information below, please help initialize the agent's needs and related parameters.

Profile Information:
- Gender: {gender}
- Education: {education} 
- Consumption Level: {consumption}
- Occupation: {occupation}
- Age: {age}
- Monthly Income: {income}
- Race: {race}
- Religion: {religion}
- Skills: {skill}

Current Time: {now_time}

Please initialize the agent's needs and parameters based on the profile above. Return the values in JSON format with the following structure:

1. Current needs satisfaction levels (0-1 float values, lower means less satisfied):
- hungry: Hunger satisfaction level (Normally, the agent will be more hungry at eating time)
- tired: Fatigue level (Normally, at night, the agent will be more tired)
- safe: Safety satisfaction level (Normally, the agent will be more safe when they have high income and currency)
- social: Social satisfaction level

2. Natural decay rates per hour (0-1 float values):
- alpha_H: Hunger satisfaction decay rate
- alpha_D: Fatigue decay rate  
- alpha_P: Safety satisfaction decay rate
- alpha_C: Social satisfaction decay rate

3. Threshold values (0-1 float values, below which the agent will try to improve):
- T_H: Hunger satisfaction threshold
- T_D: Fatigue threshold
- T_S: Safety threshold  
- T_C: Social threshold

Example response format (Do not return any other text):
{{
    "current_needs": {{
        "hungry": 0.8,
        "tired": 0.7,
        "safe": 0.9,
        "social": 0.6
    }},
    "decay_rates": {{
        "alpha_H": 0.2,
        "alpha_D": 0.08,
        "alpha_P": 0.05,
        "alpha_C": 0.03
    }},
    "thresholds": {{
        "T_H": 0.4,
        "T_D": 0.2,
        "T_S": 0.2,
        "T_C": 0.2
    }}
}}
"""

EVALUATION_PROMPT = """You are an evaluation system for an intelligent agent. The agent has performed the following actions to satisfy the {current_need} need:

Goal: {plan_target}
Execution steps:
{evaluation_results}

Current needs status: {current_needs}

Please evaluate and adjust the value of {current_need} need based on the execution results above.

Notes:
1. Need values range from 0-1, where:
   - 1 means the need is fully satisfied
   - 0 means the need is completely unsatisfied 
   - Higher values indicate greater need satisfaction
2. If the current need is not "whatever", only return the new value for the current need. Otherwise, return both safe and social need values.
3. Ensure the return value is in valid JSON format, examples below:

Example response format for specific need (hungry here) adjustment (Do not return any other text):
{{
    "hungry": new_need_value
}}

Example response format for whatever need adjustment (Do not return any other text):
{{
    "safe": new_safe_value,
    "social": new_social_value
}}
"""

class NeedsBlock(Block):
    """
    Generate needs
    """
    def __init__(self, llm: LLM, memory: Memory, simulator: Simulator):
        super().__init__("NeedsBlock", llm, memory, simulator)
        self.evaluation_prompt = FormatPrompt(EVALUATION_PROMPT)
        self.initial_prompt = FormatPrompt(INITIAL_NEEDS_PROMPT)
        self.last_evaluation_time = None
        self.trigger_time = 0
        self.token_consumption = 0
        self.initialized = False
        self.alpha_H, self.alpha_D, self.alpha_P, self.alpha_C = 0.2, 0.08, 0.05, 0.03  # 饥饿感与疲劳感自然衰减速率
        self.T_H, self.T_D, self.T_P, self.T_C = 0.4, 0.2, 0.2, 0.2  # 饥饿感与疲劳感临界值

    async def initialize(self):
        self.initial_prompt.format(
            gender=await self.memory.get("gender"),
            education=await self.memory.get("education"),
            consumption=await self.memory.get("consumption"),
            occupation=await self.memory.get("occupation"),
            age=await self.memory.get("age"),
            income=await self.memory.get("income"),
            race=await self.memory.get("race"),
            religion=await self.memory.get("religion"),
            skill=await self.memory.get("skill"),
            now_time=await self.simulator.get_time(format_time=True)
        )
        response = await self.llm.atext_request(
            self.initial_prompt.to_dialog()
        )
        response = self.clean_json_response(response)
        logger.info(f"Needs Initialization: {response}")
        try:
            needs = json.loads(response)
            await self.memory.update("needs", needs["current_needs"])
            self.alpha_H, self.alpha_D, self.alpha_P, self.alpha_C = needs["decay_rates"].values()
            self.T_H, self.T_D, self.T_P, self.T_C = needs["thresholds"].values()
        except json.JSONDecodeError:
            logger.warning(f"初始化响应不是有效的JSON格式: {response}")
        self.initialized = True

    async def forward(self):
        self.trigger_time += 1
        consumption_start = self.llm.prompt_tokens_used + self.llm.completion_tokens_used

        if not self.initialized:
            await self.initialize()

        # 计算时间差
        time_now = await self.simulator.get_time()
        if self.last_evaluation_time is None:
            self.last_evaluation_time = time_now
            time_diff = 0
        else:
            time_diff = (time_now - self.last_evaluation_time)/3600
            self.last_evaluation_time = time_now

        # 获取当前需求
        needs = await self.memory.get("needs")
        
        # 根据经过的时间计算饥饿与疲劳的衰减
        hungry_decay = self.alpha_H * time_diff
        tired_decay = self.alpha_D * time_diff
        safe_decay = self.alpha_P * time_diff
        social_decay = self.alpha_C * time_diff
        hungry = max(0, needs["hungry"] - hungry_decay) 
        tired = max(0, needs["tired"] - tired_decay)
        safe = max(0, needs["safe"] - safe_decay)
        social = max(0, needs["social"] - social_decay)
        needs["hungry"] = hungry
        needs["tired"] = tired
        needs["safe"] = safe
        needs["social"] = social

        await self.memory.update("needs", needs)

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
            await self.memory.update("current_step", {"intention": "", "type": ""})
            await self.memory.update("execution_context", {})
        
        needs = await self.memory.get("needs")
        hungry = needs["hungry"]
        tired = needs["tired"]
        safe = needs["safe"]
        social = needs["social"]
        logger.info(f"Time elapsed: {time_diff:.2f} hours")
        logger.info(f"Current state - Hungry: {hungry:.2f}, Tired: {tired:.2f}, Safe: {safe:.2f}, Social: {social:.2f}")

        # 如果需要调整需求，更新当前需求
        # 调整方案为，如果当前的需求为空，或有更高级的需求出现，则调整需求
        current_need = await self.memory.get("current_need")
        
        # 当前没有计划或计划已执行完毕，获取所有需求值，按优先级检查各需求是否达到阈值
        if not current_plan or current_plan.get("completed"):
            # 按优先级顺序检查需求
            if hungry <= self.T_H:
                await self.memory.update("current_need", "hungry")
                logger.info("Needs adjusted: Hungry")
            elif tired <= self.T_D:
                await self.memory.update("current_need", "tired") 
                logger.info("Needs adjusted: Tired")
            elif safe <= self.T_P:
                await self.memory.update("current_need", "safe")
                logger.info("Needs adjusted: Safe")
            elif social <= self.T_C:
                await self.memory.update("current_need", "social")
                logger.info("Needs adjusted: Social")
            else:
                await self.memory.update("current_need", "whatever")
                logger.info("Needs adjusted: Whatever")
        else:
            # 有正在执行的计划时,只在出现更高优先级需求时调整
            needs_changed = False
            new_need = None
            if hungry <= self.T_H and current_need not in ["hungry", "tired"]:
                new_need = "hungry"
                logger.info("Higher priority need detected, adjusted to: Hungry")
                needs_changed = True
            elif tired <= self.T_D and current_need not in ["hungry", "tired"]:
                new_need = "tired"
                logger.info("Higher priority need detected, adjusted to: Tired")
                needs_changed = True
            elif safe <= self.T_P and current_need not in ["hungry", "tired", "safe"]:
                new_need = "safe"
                logger.info("Higher priority need detected, adjusted to: Safe")
                needs_changed = True
            elif social <= self.T_C and current_need not in ["hungry", "tired", "safe", "social"]:
                new_need = "social"
                logger.info("Higher priority need detected, adjusted to: Social")
                needs_changed = True
                
            # 如果需求发生变化,中断当前计划
            if needs_changed:
                await self.evaluate_and_adjust_needs(current_plan)
                history = await self.memory.get("plan_history")
                history.append(current_plan)
                await self.memory.update("current_need", new_need)
                await self.memory.update("plan_history", history)
                await self.memory.update("current_plan", None)
                await self.memory.update("current_step", {"intention": "", "type": ""})
                await self.memory.update("execution_context", {})
                logger.info("----Agent's plan has been interrupted due to need change----")

        consumption_end = self.llm.prompt_tokens_used + self.llm.completion_tokens_used
        self.token_consumption += consumption_end - consumption_start

    async def evaluate_and_adjust_needs(self, completed_plan):
        # 获取执行的计划和评估结果
        evaluation_results = []
        for step in completed_plan["steps"]:
            if 'evaluation' in step['evaluation']:
                eva_ = step['evaluation']['evaluation']
            else:
                eva_ = 'Plan interrupted, not completed'
            evaluation_results.append(f"- {step['intention']} ({step['type']}): {eva_}")
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
            logger.info("\n=== Needs Evaluation ===")
            logger.info(f"Evaluating need: {current_need}")
            logger.info(f"Executing plan: {completed_plan['target']}")
            logger.info("Execution results:")
            logger.info(evaluation_results)
            
            new_needs = json.loads(self.clean_json_response(response)) # type: ignore
            # 更新所有需求的数值
            needs = await self.memory.get("needs")
            logger.info(f"\nNeeds value adjustment:")
            for need_type, new_value in new_needs.items():
                if need_type in needs:
                    old_value = needs[need_type]
                    needs[need_type] = new_value
                    logger.info(f"- {need_type}: {old_value} -> {new_value}")
            await self.memory.update("needs", needs)
            logger.info("===============\n")
        except json.JSONDecodeError:
            logger.warning(f"Evaluation response is not a valid JSON format: {response}")
        except Exception as e:
            logger.warning(f"Error processing evaluation response: {str(e)}")
            logger.warning(f"Original response: {response}")

    def clean_json_response(self, response: str) -> str:
        """清理LLM响应中的特殊字符"""
        response = response.replace('```json', '').replace('```', '')
        return response.strip() 