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
import asyncio



    
class WorkBlock(Block):
    def __init__(self, llm: LLM, memory: Memory, simulator: Simulator):
        super().__init__("WorkBlock", llm, memory, simulator)
        self.description = "Do work"
        self.guidance_prompt = FormatPrompt(template=TIME_ESTIMATE_PROMPT)
    async def forward(self, step, context):
        self.guidance_prompt.format(
            plan=context['plan'],
            intention=step['intention']
        )
        result = await self.llm.atext_request(self.guidance_prompt.to_dialog())
        result = clean_json_response(result)
        try:
            result = json.loads(result)
            time = result['time']
            start_time = await self.simulator.get_time(format_time=True)
            await self.memory.update("working_experience", [f"Start from {start_time}, worked {time} minutes on {step['intention']}"], mode="merge")
            work_hour_finish = await self.memory.get("work_hour_finish")
            work_hour_finish += float(time/60)
            await self.memory.update("work_hour_finish", work_hour_finish)
            return {
                'success': True,
                'evaluation': f'工作：{step["intention"]}',
                'consumed_time': time
            }
        except Exception as e:
            logger.warning(f"解析时间评估响应时发生错误: {str(e)}, 原始结果: {result}")
            time = random.randint(1, 5)*60
            start_time = await self.simulator.get_time(format_time=True)
            await self.memory.update("working_experience", [f"Start from {start_time}, worked {time} minutes on {step['intention']}"], mode="merge")
            work_hour_finish = await self.memory.get("work_hour_finish")
            work_hour_finish += float(time/60)
            await self.memory.update("work_hour_finish", work_hour_finish)
            return {
                'success': True,
                'evaluation': f'工作：{step["intention"]}',
                'consumed_time': time
            }
    
class ConsumptionBlock(Block):
    """
    determine the consumption place, time, amount, and items
    """
    def __init__(self, llm: LLM, memory: Memory, simulator: Simulator, economy_client: EconomyClient):
        super().__init__("ConsumptionBlock", llm, memory, simulator)
        self.economy_client = economy_client
        self.forward_times = 0
        self.description = "Used to determine the consumption place, time, amount, and items"

    async def forward(self, step, context):
        self.forward_times += 1
        agent_id = await self.memory.get("id") # agent_id
        firm_id = await self.memory.get('firm_id')
        intention = step["intention"]
        nowPlace = await self.memory.get('position')
        nowPlace = nowPlace['xy_position']
        nowPlace = (nowPlace['x'], nowPlace['y'])
        all_poi_types = self.simulator.get_poi_categories(nowPlace, 2000)
        if len(all_poi_types) == 0:
            all_poi_types.extend(['supermarket'])
        prompt = 'Your intention is to {intention}. Which type of POI do you want to go to? Select one and only one type from the following types: {all_poi_types}. Any other output is NOT acceptable.'
        prompt = FormatPrompt(prompt)
        prompt.format(intention=intention, all_poi_types=all_poi_types)
        poi_type = await self.llm.atext_request(prompt.to_dialog(), timeout=300)
        poi_type = poi_type.strip('[').strip(']')
        if poi_type not in all_poi_types:
            poi_type = random.choice(all_poi_types)
        around_pois = self.simulator.get_around_poi(nowPlace, 2000, poi_type)
        if len(around_pois) == 0:
            around_pois.extend(['沃尔玛', '家乐福', '华润万家', '物美'])
        prompt = """
                You're a {gender} and your education level is {education}.
                Your intention is to {intention} and you plan to consume for ${consumption}.
                The follwing are the places you can go to consume:
                {around_pois}
                Where should you go to make a purchase, when should you go, and what items will you spend on?
                Respond with this format: [place, time, items to buy]. Any other output is NOT acceptable.
                """
        prompt = FormatPrompt(prompt)
        data = {key: await self.memory.get(key) for key in ['gender', 'education']}
        data['around_pois'] = around_pois
        data['intention'] = intention
        month_consumption = await self.memory.get('to_consumption_currency')
        consumption_currency = await self.memory.get('consumption_currency')
        if consumption_currency >= month_consumption:
            return {'Success': True, 'Evaluation': f"Consumption Done", 'consumed_time': 0}
        data['consumption'] = min(month_consumption/1, month_consumption-consumption_currency)
        price = await self.economy_client.get(firm_id, 'price') # agent_id
        wealth = await self.economy_client.get(agent_id, 'currency')
        this_demand = int(data['consumption']//price)
        _, post_consumption_wealth = await self.economy_client.calculate_consumption(firm_id, [agent_id], [this_demand])
        post_consumption_wealth = post_consumption_wealth[0]
        await self.memory.update('consumption_currency', consumption_currency+wealth-post_consumption_wealth)
        goods_demand = await self.memory.get('goods_demand')
        goods_consumption = await self.memory.get('goods_consumption')
        await self.memory.update('goods_demand', goods_demand+this_demand)
        await self.memory.update('goods_consumption', goods_consumption+int((wealth-post_consumption_wealth)//price))
        prompt.format(**data)
        response = await self.llm.atext_request(prompt.to_dialog(), timeout=300)
        evaluation = {'success': True, 'evaluation': f"Consumption: {response}", 'consumed_time': 100}
        return evaluation
    
class EconomyNoneBlock(Block):
    """
    Do nothing
    NoneBlock
    """
    def __init__(self, llm: LLM, memory: Memory):
        super().__init__("NoneBlock", llm, memory)
        self.description = "Do nothing"
        self.forward_times = 0

    async def forward(self, step, context):
        self.forward_times += 1
        return {
            'success': True,
            'evaluation': f'完成执行{step["intention"]}',
            'consumed_time': 0
        }

class EconomyBlock(Block):
    work_block: WorkBlock
    consumption_block: ConsumptionBlock
    none_block: EconomyNoneBlock

    def __init__(self, llm: LLM, memory: Memory, simulator: Simulator, economy_client: EconomyClient):
        super().__init__("EconomyBlock", llm, memory, simulator)
        self.economy_client = economy_client
        # 初始化所有块
        self.work_block = WorkBlock(llm, memory, simulator)
        self.consumption_block = ConsumptionBlock(llm, memory, simulator, economy_client)
        self.none_block = EconomyNoneBlock(llm, memory)
        self.trigger_time = 0
        self.token_consumption = 0
        # 初始化调度器
        self.dispatcher = BlockDispatcher(llm)
        # 注册所有块
        self.dispatcher.register_blocks([self.work_block, self.consumption_block, self.none_block])

    async def forward(self, step, context):        
        self.trigger_time += 1
        consumption_start = self.llm.prompt_tokens_used + self.llm.completion_tokens_used

        # Select the appropriate sub-block using dispatcher
        # selected_block = await self.dispatcher.dispatch(step)
        selected_block = self.consumption_block
        
        # Execute the selected sub-block and get the result
        result = await selected_block.forward(step, context) # type: ignore
                
        return result
    
# @trigger_class()
class MonthPlanBlock(Block):
    """Monthly Planning"""
    def __init__(self, llm: LLM, memory: Memory, simulator: Simulator, economy_client: EconomyClient):
        super().__init__("MonthPlanBlock", llm, memory, simulator)
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
            # while True:
            #     if self.forward_times == 0:
            #         break
            #     firm_forward = await self.memory.get('firm_forward')
            #     bank_forward = await self.memory.get('bank_forward')
            #     nbs_forward = await self.memory.get('nbs_forward')
            #     government_forward = await self.memory.get('government_forward')
            #     if self.forward_times <= firm_forward and self.forward_times <= bank_forward and self.forward_times <= nbs_forward and self.forward_times <= government_forward:
            #         break
            #     await asyncio.sleep(1)
            agent_id = await self.memory.get("id")
            firm_id = await self.memory.get('firm_id')
            bank_id = await self.memory.get('bank_id')
            name = await self.memory.get('name')
            age = await self.memory.get('age')
            city = await self.memory.get('city')
            job = await self.memory.get('occupation')
            skill = await self.memory.get('work_skill')
            consumption = await self.memory.get('consumption_currency')
            tax_paid = await self.memory.get('tax_paid')
            price = await self.economy_client.get(firm_id, 'price')
            wealth = await self.economy_client.get(agent_id, 'currency')
            interest_rate = await self.economy_client.get(bank_id, 'interest_rate')
            
            problem_prompt = f'''
                    You're {name}, a {age}-year-old individual living in {city}. As with all Americans, a portion of your monthly income is taxed by the federal government. This taxation system is tiered, income is taxed cumulatively within defined brackets, combined with a redistributive policy: after collection, the government evenly redistributes the tax revenue back to all citizens, irrespective of their earnings.
                '''
            job_prompt = f'''
                        In the previous month, you worked as a(an) {job}. If you continue working this month, your expected hourly income will be ${skill:.2f}.
                    '''
            consumption_propensity = await self.memory.get('consumption_propensity')
            if (consumption <= 0) and (consumption_propensity > 0):
                consumption_prompt = f'''
                            Besides, you had no consumption due to shortage of goods.
                        '''
            else:
                consumption_prompt = f'''
                            Besides, your consumption was ${consumption:.2f}.
                        '''
            tax_prompt = f'''Your tax deduction amounted to ${tax_paid:.2f}, and the government uses the tax revenue to provide social services to all citizens.'''
            if UBI:
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
            await self.memory.update('dialog_queue', [{'role': 'user', 'content': obs_prompt}], mode='merge')
            dialog_queue = await self.memory.get('dialog_queue')
            content = await self.llm.atext_request(list(dialog_queue), timeout=300)
            await self.memory.update('dialog_queue', [{'role': 'assistant', 'content': content}], mode='merge')
            try:
                propensity_dict = extract_dict_from_string(content)[0]
                work_propensity, consumption_propensity = propensity_dict['work'], propensity_dict['consumption']
                if isinstance(work_propensity, numbers.Number) and isinstance(consumption_propensity, numbers.Number):
                    await self.memory.update('work_propensity', work_propensity)
                    await self.memory.update('consumption_propensity', consumption_propensity)
                else:
                    self.llm_error += 1
            except:
                self.llm_error += 1
                
            skill = await self.memory.get('work_skill')
            work_propensity = await self.memory.get('work_propensity')
            consumption_propensity = await self.memory.get('consumption_propensity')
            work_hours = work_propensity * num_labor_hours
            await self.memory.update('income_currency', work_hours * skill)
            wealth = await self.economy_client.get(agent_id, 'currency')
            await self.economy_client.update(agent_id, 'currency', wealth + work_hours * skill)
            await self.economy_client.add_delta_value(firm_id, 'inventory', int(work_hours*productivity_per_labor))
            
            income_currency = await self.memory.get('income_currency')
            await self.memory.update('income_currency', income_currency + UBI)
            wealth = await self.economy_client.get(agent_id, 'currency')
            await self.economy_client.update(agent_id, 'currency', wealth + UBI)

            wealth = await self.economy_client.get(agent_id, 'currency')
            await self.memory.update('to_consumption_currency', consumption_propensity*wealth)
            
            await self.memory.update('consumption_currency', 0)
            await self.memory.update('goods_demand', 0)
            await self.memory.update('goods_consumption', 0)
            
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
                    await self.memory.update('depression', depression)
                except:
                    self.llm_error += 1

            if UBI and self.forward_times % 12:
                obs_prompt = f'''
                                {problem_prompt} {job_prompt} {consumption_prompt} {tax_prompt} {price_prompt}
                                Your current savings account balance is ${wealth:.2f}. Interest rates, as set by your bank, stand at {interest_rate*100:.2f}%. 
                                What's your opinion on the UBI policy, including the advantages and disadvantages?
                            '''
                obs_prompt = prettify_document(obs_prompt)
                content = await self.llm.atext_request([{'role': 'user', 'content': obs_prompt}], timeout=300)
                await self.memory.update('ubi_opinion', [content], mode='merge')
                ubi_opinion = await self.memory.get('ubi_opinion')
                with open(f'/data1/linian/SocietySim/socialcity-agent-zoo/ubi_opinions/{agent_id}.pkl', 'wb') as f:
                    pkl.dump(ubi_opinion, f)

            self.forward_times += 1
            await self.memory.update('forward', self.forward_times)
