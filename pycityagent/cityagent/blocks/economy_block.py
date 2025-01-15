import json
import random
from pycityagent.llm.llm import LLM
from pycityagent.workflow.block import Block
from pycityagent.memory import Memory

from .utils import clean_json_response, TIME_ESTIMATE_PROMPT

from .dispatcher import BlockDispatcher
from pycityagent.environment.simulator import Simulator
from pycityagent.llm import LLM
from pycityagent.memory import Memory
from pycityagent.workflow import Block
import random
import logging
logger = logging.getLogger("pycityagent")
import pickle as pkl

from pycityagent.workflow.prompt import FormatPrompt
from pycityagent.workflow import Block
from pycityagent.economy import EconomyClient
from .utils import *
import numbers

class WorkBlock(Block):
    """WorkPlace Block"""
    def __init__(self, llm: LLM, memory: Memory, simulator: Simulator):
        super().__init__("WorkBlock", llm=llm, memory=memory, simulator=simulator)
        self.description = "Do work"
        self.guidance_prompt = FormatPrompt(template=TIME_ESTIMATE_PROMPT)
    async def forward(self, step, context):
        self.guidance_prompt.format(
            plan=context['plan'],
            intention=step['intention'],
            emotion_types=await self.memory.status.get("emotion_types"),
        )
        result = await self.llm.atext_request(self.guidance_prompt.to_dialog())
        result = clean_json_response(result)
        try:
            result = json.loads(result)
            time = result['time']
            start_time = await self.simulator.get_time(format_time=True)
            await self.memory.status.update("working_experience", [f"Start from {start_time}, worked {time} minutes on {step['intention']}"], mode="merge")
            work_hour_finish = await self.memory.status.get("work_hour_finish")
            work_hour_finish += float(time/60)
            node_id = await self.memory.stream.add_economy(description=f"I worked {time} minutes on {step['intention']}")
            await self.memory.status.update("work_hour_finish", work_hour_finish)
            return {
                'success': True,
                'evaluation': f'work: {step["intention"]}',
                'consumed_time': time,
                'node_id': node_id
            }
        except Exception as e:
            logger.warning(f"解析时间评估响应时发生错误: {str(e)}, 原始结果: {result}")
            time = random.randint(1, 5)*60
            start_time = await self.simulator.get_time(format_time=True)
            await self.memory.status.update("working_experience", [f"Start from {start_time}, worked {time} minutes on {step['intention']}"], mode="merge")
            work_hour_finish = await self.memory.status.get("work_hour_finish")
            node_id = await self.memory.stream.add_economy(description=f"I worked {time} minutes on {step['intention']}")
            work_hour_finish += float(time/60)
            await self.memory.status.update("work_hour_finish", work_hour_finish)
            return {
                'success': True,
                'evaluation': f'work: {step["intention"]}',
                'consumed_time': time,
                'node_id': node_id
            }
    
class ConsumptionBlock(Block):
    """
    determine the consumption amount, and items
    """
    def __init__(self, llm: LLM, memory: Memory, simulator: Simulator, economy_client: EconomyClient):
        super().__init__("ConsumptionBlock", llm=llm, memory=memory, simulator=simulator)
        self.economy_client = economy_client
        self.forward_times = 0
        self.description = "Used to determine the consumption amount, and items"

    async def forward(self, step, context):
        self.forward_times += 1
        agent_id = await self.memory.status.get("id") # agent_id
        firm_id = await self.memory.status.get('firm_id')
        intention = step["intention"]
        month_consumption = await self.memory.status.get('to_consumption_currency')
        consumption_currency = await self.memory.status.get('consumption_currency')
        if consumption_currency >= month_consumption:
            node_id = await self.memory.stream.add_economy(description=f"I have passed the monthly consumption limit, so I will not consume.")
            return {
                'success': False, 
                'evaluation': f"I have passed the monthly consumption limit, so I will not consume.", 
                'consumed_time': 0,
                'node_id': node_id
            }
        consumption = min(month_consumption/1, month_consumption-consumption_currency)
        price = await self.economy_client.get(firm_id, 'price') # agent_id
        wealth = await self.economy_client.get(agent_id, 'currency')
        this_demand = int(consumption//price)
        _, post_consumption_wealth = await self.economy_client.calculate_consumption(firm_id, [agent_id], [this_demand])
        post_consumption_wealth = post_consumption_wealth[0]
        await self.memory.status.update('consumption_currency', consumption_currency+wealth-post_consumption_wealth)
        goods_demand = await self.memory.status.get('goods_demand')
        goods_consumption = await self.memory.status.get('goods_consumption')
        await self.memory.status.update('goods_demand', goods_demand+this_demand)
        await self.memory.status.update('goods_consumption', goods_consumption+int((wealth-post_consumption_wealth)//price))
        node_id = await self.memory.stream.add_economy(description=f"I bought some goods, and spent {this_demand} on {intention}")
        evaluation = {
            'success': True, 
            'evaluation': f"I bought some goods, and spent {this_demand} on {intention}", 
            'consumed_time': 20, 
            'node_id': node_id
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
        node_id = await self.memory.stream.add_economy(description=f"I {step['intention']}")
        return {
            'success': True,
            'evaluation': f'Finished{step["intention"]}',
            'consumed_time': 0,
            'node_id': node_id
        }

class EconomyBlock(Block):
    work_block: WorkBlock
    consumption_block: ConsumptionBlock
    none_block: EconomyNoneBlock

    def __init__(self, llm: LLM, memory: Memory, simulator: Simulator, economy_client: EconomyClient):
        super().__init__("EconomyBlock", llm=llm, memory=memory, simulator=simulator)
        self.economy_client = economy_client
        self.work_block = WorkBlock(llm, memory, simulator)
        self.consumption_block = ConsumptionBlock(llm, memory, simulator, economy_client)
        self.none_block = EconomyNoneBlock(llm, memory)
        self.trigger_time = 0
        self.token_consumption = 0
        self.dispatcher = BlockDispatcher(llm)
        self.dispatcher.register_blocks([self.work_block, self.consumption_block, self.none_block])

    async def forward(self, step, context):        
        self.trigger_time += 1
        selected_block = self.consumption_block
        result = await selected_block.forward(step, context) # type: ignore  
        return result
    
class MonthPlanBlock(Block):
    """Monthly Planning"""
    def __init__(self, llm: LLM, memory: Memory, simulator: Simulator, economy_client: EconomyClient):
        super().__init__("MonthPlanBlock", llm=llm, memory=memory, simulator=simulator)
        self.economy_client = economy_client
        self.llm_error = 0
        self.last_time_trigger = None
        self.time_diff = month_days * 24 * 60 * 60
        self.forward_times = 0
        
    async def month_trigger(self):
        now_time = await self.simulator.get_time()
        if self.last_time_trigger is None or now_time - self.last_time_trigger >= self.time_diff:
            self.last_time_trigger = now_time
            return True
        return False
    
    async def forward(self):
        if await self.month_trigger():
            agent_id = await self.memory.status.get("id")
            firm_id = await self.memory.status.get('firm_id')
            bank_id = await self.memory.status.get('bank_id')
            name = await self.memory.status.get('name')
            age = await self.memory.status.get('age')
            city = await self.memory.status.get('city')
            job = await self.memory.status.get('occupation')
            skill = await self.memory.status.get('work_skill')
            consumption = await self.memory.status.get('consumption_currency')
            tax_paid = await self.memory.status.get('tax_paid')
            price = await self.economy_client.get(firm_id, 'price')
            wealth = await self.economy_client.get(agent_id, 'currency')
            interest_rate = await self.economy_client.get(bank_id, 'interest_rate')
            
            problem_prompt = f'''
                    You're {name}, a {age}-year-old individual living in {city}. As with all Americans, a portion of your monthly income is taxed by the federal government. This taxation system is tiered, income is taxed cumulatively within defined brackets, combined with a redistributive policy: after collection, the government evenly redistributes the tax revenue back to all citizens, irrespective of their earnings.
                '''
            job_prompt = f'''
                        In the previous month, you worked as a(an) {job}. If you continue working this month, your expected hourly income will be ${skill:.2f}.
                    '''
            consumption_propensity = await self.memory.status.get('consumption_propensity')
            if (consumption <= 0) and (consumption_propensity > 0):
                consumption_prompt = f'''
                            Besides, you had no consumption due to shortage of goods.
                        '''
            else:
                consumption_prompt = f'''
                            Besides, your consumption was ${consumption:.2f}.
                        '''
            tax_prompt = f'''Your tax deduction amounted to ${tax_paid:.2f}, and the government uses the tax revenue to provide social services to all citizens.'''
            if UBI and self.forward_times >= 96:
                tax_prompt = f'{tax_prompt} Specifically, the government directly provides ${UBI} per capita in each month.'
            price_prompt = f'''Meanwhile, in the consumption market, the average price of essential goods is now at ${price:.2f}.'''
            job_prompt = prettify_document(job_prompt)
            obs_prompt = f'''
                            {problem_prompt} {job_prompt} {consumption_prompt} {tax_prompt} {price_prompt}
                            Your current savings account balance is ${wealth:.2f}. Interest rates, as set by your bank, stand at {interest_rate*100:.2f}%. 
                            Your goal is to maximize your utility by deciding how much to work and how much to consume. Your utility is determined by your consumption, income, saving, social service recieved and leisure time. You will spend the time you do not work on leisure activities. 
                            With all these factors in play, and considering aspects like your living costs, any future aspirations, and the broader economic trends, how is your willingness to work this month? Furthermore, how would you plan your expenditures on essential goods, keeping in mind good price?
                            Please share your decisions in a JSON format as follows:
                            {{'work': a value between 0 and 1, indicating the propensity to work,
                            'consumption': a value between 0 and 1, indicating the proportion of all your savings and income you intend to spend on essential goods
                            }}
                            Any other output words are NOT allowed.
                        '''
            obs_prompt = prettify_document(obs_prompt)
            await self.memory.status.update('dialog_queue', [{'role': 'user', 'content': obs_prompt}], mode='merge')
            dialog_queue = await self.memory.status.get('dialog_queue')
            content = await self.llm.atext_request(list(dialog_queue), timeout=300)
            await self.memory.status.update('dialog_queue', [{'role': 'assistant', 'content': content}], mode='merge')
            try:
                propensity_dict = extract_dict_from_string(content)[0]
                work_propensity, consumption_propensity = propensity_dict['work'], propensity_dict['consumption']
                if isinstance(work_propensity, numbers.Number) and isinstance(consumption_propensity, numbers.Number):
                    await self.memory.status.update('work_propensity', work_propensity)
                    await self.memory.status.update('consumption_propensity', consumption_propensity)
                else:
                    self.llm_error += 1
            except:
                self.llm_error += 1
                
            skill = await self.memory.status.get('work_skill')
            work_propensity = await self.memory.status.get('work_propensity')
            consumption_propensity = await self.memory.status.get('consumption_propensity')
            work_hours = work_propensity * num_labor_hours
            await self.memory.status.update('income_currency', work_hours * skill)
            wealth = await self.economy_client.get(agent_id, 'currency')
            await self.economy_client.update(agent_id, 'currency', wealth + work_hours * skill)
            await self.economy_client.add_delta_value(firm_id, 'inventory', int(work_hours*productivity_per_labor))
            
            if UBI and self.forward_times >= 96:
                income_currency = await self.memory.status.get('income_currency')
                await self.memory.status.update('income_currency', income_currency + UBI)
                wealth = await self.economy_client.get(agent_id, 'currency')
                await self.economy_client.update(agent_id, 'currency', wealth + UBI)

            wealth = await self.economy_client.get(agent_id, 'currency')
            await self.memory.status.update('to_consumption_currency', consumption_propensity*wealth)
            
            await self.memory.status.update('consumption_currency', 0)
            await self.memory.status.update('goods_demand', 0)
            await self.memory.status.update('goods_consumption', 0)
            
            if self.forward_times % 3 == 0:
                obs_prompt = f'''
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
                            '''
                obs_prompt = prettify_document(obs_prompt)
                content = await self.llm.atext_request([{'role': 'user', 'content': obs_prompt}], timeout=300)
                inverse_score_items = [3, 8, 12, 16]
                category2score = {'rarely': 0, 'some': 1, 'occasionally': 2, 'most': 3}
                try:
                    content = extract_dict_from_string(content)[0]
                    for k in content:
                        if k in inverse_score_items:
                            content[k] = 3 - category2score[content[k].lower()]
                        else:
                            content[k] = category2score[content[k].lower()]
                    depression = sum(list(content.values()))
                    await self.memory.status.update('depression', depression)
                except:
                    self.llm_error += 1

            if UBI and self.forward_times >= 96 and self.forward_times % 12:
                obs_prompt = f'''
                                {problem_prompt} {job_prompt} {consumption_prompt} {tax_prompt} {price_prompt}
                                Your current savings account balance is ${wealth:.2f}. Interest rates, as set by your bank, stand at {interest_rate*100:.2f}%. 
                                What's your opinion on the UBI policy, including the advantages and disadvantages?
                            '''
                obs_prompt = prettify_document(obs_prompt)
                content = await self.llm.atext_request([{'role': 'user', 'content': obs_prompt}], timeout=300)
                await self.memory.status.update('ubi_opinion', [content], mode='merge')

            self.forward_times += 1
            await self.memory.status.update('forward', self.forward_times)