import asyncio
import json
import logging
import numbers
import pickle as pkl
import random

import numpy as np
import pycityproto.city.economy.v2.economy_pb2 as economyv2

from agentsociety.environment import EconomyClient
from agentsociety.environment.simulator import Simulator
from agentsociety.llm import LLM
from agentsociety.llm.llm import LLM
from agentsociety.memory import Memory
from agentsociety.workflow import Block
from agentsociety.workflow.block import Block
from agentsociety.workflow.prompt import FormatPrompt

from .dispatcher import BlockDispatcher
from .utils import *
from .utils import TIME_ESTIMATE_PROMPT, clean_json_response

logger = logging.getLogger("agentsociety")

def softmax(x, gamma=1.0):
    if not isinstance(x, np.ndarray):
        x = np.array(x)
    x *= gamma
    e_x = np.exp(x - np.max(x))
    return e_x / e_x.sum(axis=-1, keepdims=True)


class WorkBlock(Block):
    """WorkPlace Block"""

    def __init__(self, llm: LLM, memory: Memory, simulator: Simulator):
        super().__init__("WorkBlock", llm=llm, memory=memory, simulator=simulator)
        self.description = "Do work related tasks"
        self.guidance_prompt = FormatPrompt(template=TIME_ESTIMATE_PROMPT)

    async def forward(self, step, context):
        self.guidance_prompt.format(
            plan=context["plan"],
            intention=step["intention"],
            emotion_types=await self.memory.status.get("emotion_types"),
        )
        result = await self.llm.atext_request(self.guidance_prompt.to_dialog(), response_format={"type": "json_object"})
        result = clean_json_response(result)
        try:
            result = json.loads(result)
            time = result["time"]
            start_time = await self.simulator.get_time(format_time=True)
            await self.memory.status.update(
                "working_experience",
                [
                    f"Start from {start_time}, worked {time} minutes on {step['intention']}"
                ],
                mode="merge",
            )
            work_hour_finish = await self.memory.status.get("work_hour_finish")
            work_hour_finish += float(time / 60)
            node_id = await self.memory.stream.add_economy(
                description=f"I worked {time} minutes on {step['intention']}"
            )
            await self.memory.status.update("work_hour_finish", work_hour_finish)
            return {
                "success": True,
                "evaluation": f'work: {step["intention"]}',
                "consumed_time": time,
                "node_id": node_id,
            }
        except Exception as e:
            logger.warning(f"解析时间评估响应时发生错误: {str(e)}, 原始结果: {result}")
            time = random.randint(1, 5) * 60
            start_time = await self.simulator.get_time(format_time=True)
            await self.memory.status.update(
                "working_experience",
                [
                    f"Start from {start_time}, worked {time} minutes on {step['intention']}"
                ],
                mode="merge",
            )
            work_hour_finish = await self.memory.status.get("work_hour_finish")
            node_id = await self.memory.stream.add_economy(
                description=f"I worked {time} minutes on {step['intention']}"
            )
            work_hour_finish += float(time / 60)
            await self.memory.status.update("work_hour_finish", work_hour_finish)
            return {
                "success": True,
                "evaluation": f'work: {step["intention"]}',
                "consumed_time": time,
                "node_id": node_id,
            }


class ConsumptionBlock(Block):
    """
    determine the consumption amount, and items
    """

    def __init__(
        self,
        llm: LLM,
        memory: Memory,
        simulator: Simulator,
        economy_client: EconomyClient,
    ):
        super().__init__(
            "ConsumptionBlock", llm=llm, memory=memory, simulator=simulator
        )
        self.economy_client = economy_client
        self.forward_times = 0
        self.description = "Used to determine the consumption amount, and items"

    async def forward(self, step, context):
        self.forward_times += 1
        agent_id = await self.memory.status.get("id")  # agent_id
        firms_id = await self.economy_client.get_org_entity_ids(economyv2.ORG_TYPE_FIRM)
        intention = step["intention"]
        month_consumption = await self.memory.status.get("to_consumption_currency")
        consumption_currency = await self.economy_client.get(agent_id, "consumption")
        if consumption_currency >= month_consumption:
            node_id = await self.memory.stream.add_economy(
                description=f"I have passed the monthly consumption limit, so I will not consume."
            )
            return {
                "success": False,
                "evaluation": f"I have passed the monthly consumption limit, so I will not consume.",
                "consumed_time": 0,
                "node_id": node_id,
            }
        consumption = min(
            month_consumption / 1, month_consumption - consumption_currency
        )
        prices = []
        for this_firm_id in firms_id:
            price = await self.economy_client.get(this_firm_id, "price")
            prices.append(price)
        consumption_each_firm = consumption * softmax(prices, gamma=-0.01)
        demand_each_firm = []
        for i in range(len(firms_id)):
            demand_each_firm.append(int(consumption_each_firm[i] // prices[i]))
        real_consumption = await self.economy_client.calculate_consumption(
            firms_id, agent_id, demand_each_firm
        )
        node_id = await self.memory.stream.add_economy(
            description=f"I bought some goods, and spent {real_consumption:.1f} on {intention}"
        )
        evaluation = {
            "success": True,
            "evaluation": f"I bought some goods, and spent {real_consumption:.1f} on {intention}",
            "consumed_time": 20,
            "node_id": node_id,
        }
        return evaluation


class EconomyNoneBlock(Block):
    """
    Do anything else
    NoneBlock
    """

    def __init__(self, llm: LLM, memory: Memory):
        super().__init__("NoneBlock", llm=llm, memory=memory)
        self.description = "Do anything else"

    async def forward(self, step, context):
        node_id = await self.memory.stream.add_economy(
            description=f"I {step['intention']}"
        )
        return {
            "success": True,
            "evaluation": f'Finished{step["intention"]}',
            "consumed_time": 0,
            "node_id": node_id,
        }


class EconomyBlock(Block):
    work_block: WorkBlock
    consumption_block: ConsumptionBlock
    none_block: EconomyNoneBlock

    def __init__(
        self,
        llm: LLM,
        memory: Memory,
        simulator: Simulator,
        economy_client: EconomyClient,
    ):
        super().__init__("EconomyBlock", llm=llm, memory=memory, simulator=simulator)
        self.economy_client = economy_client
        self.work_block = WorkBlock(llm, memory, simulator)
        self.consumption_block = ConsumptionBlock(
            llm, memory, simulator, economy_client
        )
        self.none_block = EconomyNoneBlock(llm, memory)
        self.trigger_time = 0
        self.token_consumption = 0
        self.dispatcher = BlockDispatcher(llm)
        self.dispatcher.register_blocks(
            [self.work_block, self.consumption_block, self.none_block]
        )

    async def forward(self, step, context):
        self.trigger_time += 1
        selected_block = await self.dispatcher.dispatch(step)
        result = await selected_block.forward(step, context)  # type: ignore
        return result


class MonthPlanBlock(Block):
    """Monthly Planning"""

    configurable_fields = [
        "UBI",
        "num_labor_hours",
        "productivity_per_labor",
        "time_diff",
    ]
    default_values = {
        "UBI": 0,
        "num_labor_hours": 168,
        "productivity_per_labor": 1,
        "time_diff": 30 * 24 * 60 * 60,
    }
    fields_description = {
        "UBI": "Universal Basic Income",
        "num_labor_hours": "Number of labor hours per month",
        "productivity_per_labor": "Productivity per labor hour",
        "time_diff": "Time difference between two triggers",
    }

    def __init__(
        self,
        llm: LLM,
        memory: Memory,
        simulator: Simulator,
        economy_client: EconomyClient,
    ):
        super().__init__("MonthPlanBlock", llm=llm, memory=memory, simulator=simulator)
        self.economy_client = economy_client
        self.llm_error = 0
        self.last_time_trigger = None
        self.forward_times = 0

        # configurable fields
        self.UBI = 0
        self.num_labor_hours = 168
        self.productivity_per_labor = 1
        self.time_diff = 30 * 24 * 60 * 60

    async def month_trigger(self):
        now_time = await self.simulator.get_time()
        if (
            self.last_time_trigger is None
            or now_time - self.last_time_trigger >= self.time_diff
        ):
            self.last_time_trigger = now_time
            return True
        return False

    async def forward(self):
        if await self.month_trigger():
            agent_id = await self.memory.status.get("id")
            firms_id = await self.economy_client.get_org_entity_ids(
                economyv2.ORG_TYPE_FIRM
            )
            firm_id = await self.memory.status.get("firm_id")
            bank_id = await self.economy_client.get_org_entity_ids(
                economyv2.ORG_TYPE_BANK
            )
            bank_id = bank_id[0]
            name = await self.memory.status.get("name")
            age = await self.memory.status.get("age")
            city = await self.memory.status.get("city")
            job = await self.memory.status.get("occupation")
            skill = await self.economy_client.get(agent_id, "skill")
            consumption = await self.economy_client.get(agent_id, "consumption")
            tax_paid = await self.memory.status.get("tax_paid")
            prices = []
            for this_firm_id in firms_id:
                price = await self.economy_client.get(this_firm_id, "price")
                prices.append(price)
            price = np.mean(prices)
            wealth = await self.economy_client.get(agent_id, "currency")
            interest_rate = await self.economy_client.get(bank_id, "interest_rate")

            problem_prompt = f"""
                    You're {name}, a {age}-year-old individual living in {city}. As with all Americans, a portion of your monthly income is taxed by the federal government. This taxation system is tiered, income is taxed cumulatively within defined brackets, combined with a redistributive policy: after collection, the government evenly redistributes the tax revenue back to all citizens, irrespective of their earnings.
                """
            job_prompt = f"""
                        In the previous month, you worked as a(an) {job}. If you continue working this month, your expected hourly income will be ${skill:.2f}.
                    """
            consumption_propensity = await self.memory.status.get(
                "consumption_propensity"
            )
            if (consumption <= 0) and (consumption_propensity > 0):
                consumption_prompt = f"""
                            Besides, you had no consumption due to shortage of goods.
                        """
            else:
                consumption_prompt = f"""
                            Besides, your consumption was ${consumption:.2f}.
                        """
            tax_prompt = f"""Your tax deduction amounted to ${tax_paid:.2f}, and the government uses the tax revenue to provide social services to all citizens."""
            if self.UBI and self.forward_times >= 96:
                tax_prompt = f"{tax_prompt} Specifically, the government directly provides ${self.UBI} per capita in each month."
            price_prompt = f"""Meanwhile, in the consumption market, the average price of essential goods is now at ${price:.2f}."""
            job_prompt = prettify_document(job_prompt)
            obs_prompt = f"""
                            {problem_prompt} {job_prompt} {consumption_prompt} {tax_prompt} {price_prompt}
                            Your current savings account balance is ${wealth:.2f}. Interest rates, as set by your bank, stand at {interest_rate*100:.2f}%. 
                            Your goal is to maximize your utility by deciding how much to work and how much to consume. Your utility is determined by your consumption, income, saving, social service recieved and leisure time. You will spend the time you do not work on leisure activities. 
                            With all these factors in play, and considering aspects like your living costs, any future aspirations, and the broader economic trends, how is your willingness to work this month? Furthermore, how would you plan your expenditures on essential goods, keeping in mind good price?
                            Please share your decisions in a JSON format as follows:
                            {{'work': a value between 0 and 1, indicating the propensity to work,
                            'consumption': a value between 0 and 1, indicating the proportion of all your savings and income you intend to spend on essential goods
                            }}
                            Any other output words are NOT allowed.
                        """
            obs_prompt = prettify_document(obs_prompt)
            try:
                await self.memory.status.update(
                    "dialog_queue",
                    [{"role": "user", "content": obs_prompt}],
                    mode="merge",
                )
                dialog_queue = await self.memory.status.get("dialog_queue")
                content = await self.llm.atext_request(list(dialog_queue), timeout=300)
                await self.memory.status.update(
                    "dialog_queue",
                    [{"role": "assistant", "content": content}],
                    mode="merge",
                )
                propensity_dict = extract_dict_from_string(content)[0]
                work_propensity, consumption_propensity = (
                    propensity_dict["work"],
                    propensity_dict["consumption"],
                )
                if isinstance(work_propensity, numbers.Number) and isinstance(
                    consumption_propensity, numbers.Number
                ):
                    await self.memory.status.update("work_propensity", work_propensity)
                    await self.memory.status.update(
                        "consumption_propensity", consumption_propensity
                    )
                else:
                    self.llm_error += 1
            except:
                self.llm_error += 1

            work_skill = await self.economy_client.get(agent_id, "skill")
            work_propensity = await self.memory.status.get("work_propensity")
            consumption_propensity = await self.memory.status.get(
                "consumption_propensity"
            )
            work_hours = work_propensity * self.num_labor_hours
            # income = await self.economy_client.get(agent_id, 'income')
            income = work_hours * work_skill

            wealth = await self.economy_client.get(agent_id, "currency")
            wealth += work_hours * work_skill
            await self.economy_client.update(agent_id, "currency", wealth)
            await self.economy_client.add_delta_value(
                firm_id, "inventory", int(work_hours * self.productivity_per_labor)
            )

            if self.UBI and self.forward_times >= 96:
                income += self.UBI
                wealth += self.UBI

            await self.memory.status.update(
                "to_consumption_currency", consumption_propensity * wealth
            )

            await self.economy_client.update(agent_id, "consumption", 0)
            await self.economy_client.update(agent_id, "income", income)
            await self.economy_client.update(agent_id, "currency", wealth)

            if self.forward_times % 3 == 0:
                obs_prompt = f"""
                                {problem_prompt} {job_prompt} {consumption_prompt} {tax_prompt} {price_prompt}
                                Your current savings account balance is ${wealth:.2f}. Interest rates, as set by your bank, stand at {interest_rate*100:.2f}%. 
                                Please fill in the following questionnaire:
                                Indicate how often you have felt this way during the last week by choosing one of the following options:
                                "Rarely" means Rarely or none of the time (less than 1 day),
                                "Some" means Some or a little of the time (1-2 days),
                                "Occasionally" means Occasionally or a moderate amount of the time (3-4 days),
                                "Most" means Most or all of the time (5-7 days).
                                Statement 1: I was bothered by things that usually don't bother me.  
                                Statement 2: I did not feel like eating; my appetite was poor.
                                Statement 3: I felt that I could not shake off the blues even with help from my family or friends.
                                Statement 4: I felt that I was just as good as other people.
                                Statement 5: I had trouble keeping my mind on what I was doing.
                                Statement 6: I felt depressed.
                                Statement 7: I felt that everything I did was an effort.
                                Statement 8: I felt hopeful about the future.
                                Statement 9: I thought my life had been a failure.
                                Statement 10: I felt fearful.
                                Statement 11: My sleep was restless.
                                Statement 12: I was happy.
                                Statement 13: I talked less than usual.
                                Statement 14: I felt lonely.
                                Statement 15: People were unfriendly.
                                Statement 16: I enjoyed life.
                                Statement 17: I had crying spells.
                                Statement 18: I felt sad.
                                Statement 19: I felt that people disliked me.
                                Statement 20: I could not get "going".
                                Please response with json format with keys being numbers 1-20 and values being one of "Rarely", "Some", "Occasionally", "Most".
                                Any other output words are NOT allowed.
                            """
                obs_prompt = prettify_document(obs_prompt)
                content = await self.llm.atext_request(
                    [{"role": "user", "content": obs_prompt}], timeout=300
                )
                inverse_score_items = [3, 8, 12, 16]
                category2score = {"rarely": 0, "some": 1, "occasionally": 2, "most": 3}
                try:
                    content = extract_dict_from_string(content)[0]
                    for k in content:
                        if k in inverse_score_items:
                            content[k] = 3 - category2score[content[k].lower()]
                        else:
                            content[k] = category2score[content[k].lower()]
                    depression = sum(list(content.values()))
                    await self.memory.status.update("depression", depression)
                except:
                    self.llm_error += 1

            if self.UBI and self.forward_times >= 96 and self.forward_times % 12 == 0:
                obs_prompt = f"""
                                {problem_prompt} {job_prompt} {consumption_prompt} {tax_prompt} {price_prompt}
                                Your current savings account balance is ${wealth:.2f}. Interest rates, as set by your bank, stand at {interest_rate*100:.2f}%. 
                                What's your opinion on the UBI policy, including the advantages and disadvantages?
                            """
                obs_prompt = prettify_document(obs_prompt)
                content = await self.llm.atext_request(
                    [{"role": "user", "content": obs_prompt}], timeout=300
                )
                await self.memory.status.update("ubi_opinion", [content], mode="merge")

            self.forward_times += 1
