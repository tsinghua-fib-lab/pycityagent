import json
from pycityagent.workflow import Block
from pycityagent.llm import LLM
from pycityagent.memory import Memory
from pycityagent.workflow.prompt import FormatPrompt

GUIDANCE_OPTIONS = {
    "hungry": ["在家吃饭", "外出吃饭"],
    "tired": ["睡觉"],
    "safe": ["工作", "购物"],
    "social": ["线上社交", "购物"],
}

GUIDANCE_SELECTION_PROMPT = """作为一个智能体的决策系统，请从以下可选方案中选择一个最适合的方案来满足当前需求。

当前需求: {current_need}
可选方案: {options}

请从以下三个维度进行评估并选择最合适的方案：
1. 态度(Attitude): 对该方案的个人喜好和评价
2. 主观规范(Subjective Norm): 社会环境和他人对该行为的看法
3. 感知控制(Perceived Control): 执行该方案的难度和可控性

请以JSON格式返回评估结果：
{{
    "selected_option": "选择的方案",
    "evaluation": {{
        "attitude": "对方案的态度评分(0-1)",
        "subjective_norm": "主观规范评分(0-1)",
        "perceived_control": "感知控制评分(0-1)",
        "reasoning": "选择该方案的���体原因"
    }}
}}
"""

DETAILED_PLAN_PROMPT = """基于选定的指导方案，生成具体的执行步骤。

当前需求: {current_need}
选定方案: {selected_option}
当前位置: {current_location}
家的位置: {home_location}
工作地点: {work_location}

请生成具体的执行步骤，以JSON格式返回：
{{
    "plan": {{
        "target": "具体目标",
        "steps": [
            {{
                "intention": "具体意图",
                "type": "步骤类型"
            }}
        ]
    }}
}}

注意：
1. type只能是以下四种之一：mobility, social, economy, other
    1.1 mobility：对应所有与移动相关的决策或行为，例如地点选择、前往某个地点等
    1.2 social：对应所有与社交相关的决策或行为，例如找联系人，与朋友聊天等
    1.3 economy：对应所有与经济相关的决策或行为，例如购物、支付等
    1.4 other：对应其他类型的决策或行为，例如学习、休息等
2. steps中仅包含为满足target所必须的步骤(限制在6个步骤以内)
3. step中的intention应尽量精简明了

示例输出:
{{
    "plan": {{
        "target": "在家吃饭",
        "steps": [
            {{
                "intention": "从当前位置回家",
                "type": "mobility"
            }},
            {{
                "intention": "烹饪",
                "type": "other"
            }},
            {{
                "intention": "吃饭",
                "type": "other"
            }}
        ]
    }}
}}

{{
    "plan": {{
        "target": "外出吃饭", 
        "steps": [
            {{
                "intention": "选择餐厅",
                "type": "mobility"
            }},
            {{
                "intention": "前往餐厅",
                "type": "mobility"
            }},
            {{
                "intention": "点餐",
                "type": "economy"
            }},
            {{
                "intention": "用餐",
                "type": "other"
            }}
        ]
    }}
}}

{{
    "plan": {{
        "target": "线下社交",
        "steps": [
            {{
                "intention": "联系朋友约定见面地点",
                "type": "social"
            }},
            {{
                "intention": "前往约定地点",
                "type": "mobility"
            }},
            {{
                "intention": "与朋友交谈",
                "type": "social"
            }}
        ]
    }}
}}

{{
    "plan": {{
        "target": "工作",
        "steps": [
            {{
                "intention": "前往工作地点",
                "type": "mobility"
            }},
            {{
                "intention": "工作",
                "type": "other"
            }}
        ]
    }}
}}
"""


class PlanBlock(Block):
    def __init__(self, llm: LLM, memory: Memory):
        self.llm = llm
        self.memory = memory
        self.guidance_prompt = FormatPrompt(template=GUIDANCE_SELECTION_PROMPT)
        self.detail_prompt = FormatPrompt(template=DETAILED_PLAN_PROMPT)

    async def select_guidance(self, current_need: str) -> dict:
        """选择指导方案"""
        options = GUIDANCE_OPTIONS.get(current_need, [])
        if not options:
            return None  # type: ignore

        self.guidance_prompt.format(current_need=current_need, options=options)

        response = await self.llm.atext_request(
            self.guidance_prompt.to_dialog()
        )  # type: ignore

        try:
            result = json.loads(self.clean_json_response(response))  # type: ignore
            print(f"\n=== 方案选择 ===")
            print(f"选定方案: {result['selected_option']}")
            print(f"评估结果:")
            print(f"    - 态度: {result['evaluation']['attitude']}")
            print(f"    - 主观规范: {result['evaluation']['subjective_norm']}")
            print(f"    - 感知控制: {result['evaluation']['perceived_control']}")
            print(f"    - 选择原因: {result['evaluation']['reasoning']}")
            return result
        except Exception as e:
            print(f"解析方案选择响应时发生错误: {str(e)}")
            return None  # type: ignore

    async def generate_detailed_plan(
        self, current_need: str, selected_option: str
    ) -> dict:
        """生成具体执行计划"""
        current_location = await self.memory.get("nowPlace")
        home_location = await self.memory.get("home")
        work_location = await self.memory.get("work")

        self.detail_prompt.format(
            current_need=current_need,
            selected_option=selected_option,
            current_location=current_location,
            home_location=home_location,
            work_location=work_location,
        )

        response = await self.llm.atext_request(self.detail_prompt.to_dialog())

        try:
            result = json.loads(self.clean_json_response(response))  # type: ignore
            return result
        except Exception as e:
            print(f"解析具体计划时发生错误: {str(e)}")
            return None  # type: ignore

    async def forward(self):
        current_need = await self.memory.get("current_need")
        if current_need == "none":
            await self.memory.update("current_plan", [])
            await self.memory.update("current_step", {"intention": "", "type": ""})
            return

        # 第一步：选择指导方案
        guidance_result = await self.select_guidance(current_need)
        if not guidance_result:
            return

        # 第二步：生成具体计划
        detailed_plan = await self.generate_detailed_plan(
            current_need, guidance_result["selected_option"]
        )

        if not detailed_plan or "plan" not in detailed_plan:
            await self.memory.update("current_plan", [])
            await self.memory.update("current_step", {"intention": "", "type": ""})
            return
        print("\n=== 生成计划 ===")
        print(f"目标: {detailed_plan['plan']['target']}")
        print("\n执行步骤:")
        for i, step in enumerate(detailed_plan["plan"]["steps"], 1):
            print(f"{i}. {step['intention']} ({step['type']})")
        print("===============\n")

        # 更新计划和当前步骤
        steps = detailed_plan["plan"]["steps"]
        for step in steps:
            step["evaluation"] = {"status": "pending", "details": ""}

        plan = {
            "target": detailed_plan["plan"]["target"],
            "steps": steps,
            "completed": False,
            "guidance": guidance_result,  # 保存方案选择的评估结果
        }

        await self.memory.update("current_plan", plan)
        await self.memory.update(
            "current_step", steps[0] if steps else {"intention": "", "type": ""}
        )
        await self.memory.update("execution_context", {})

    def clean_json_response(self, response: str) -> str:
        """清理LLM响应中的特殊字符"""
        response = response.replace("```json", "").replace("```", "")
        return response.strip()
