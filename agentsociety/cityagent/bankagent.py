import asyncio
from typing import Optional

import numpy as np
from agentsociety import Simulator, InstitutionAgent
from agentsociety.llm.llm import LLM
from agentsociety.environment import EconomyClient
from agentsociety.message import Messager
from agentsociety.memory import Memory
import logging
import pycityproto.city.economy.v2.economy_pb2 as economyv2

logger = logging.getLogger("agentsociety")

def calculate_inflation(prices):
    # Make sure the length of price data is a multiple of 12
    length = len(prices)
    months_in_year = 12
    full_years = length // months_in_year  # Calculate number of complete years
    
    # Remaining data not used in calculation
    prices = prices[:full_years * months_in_year]
    
    # Group by year, calculate average price for each year
    annual_avg_prices = np.mean(np.reshape(prices, (-1, months_in_year)), axis=1)
    
    # Calculate annual inflation rates
    inflation_rates = []
    for i in range(1, full_years):
        inflation_rate = ((annual_avg_prices[i] - annual_avg_prices[i - 1]) / annual_avg_prices[i - 1]) * 100
        inflation_rates.append(inflation_rate)
    
    return inflation_rates

class BankAgent(InstitutionAgent):
    configurable_fields = ["time_diff"]
    default_values = {
        "time_diff": 30 * 24 * 60 * 60,
    }
    fields_description = {
        "time_diff": "Time difference between each forward, day * hour * minute * second",
    }
    
    def __init__(
        self,
        name: str,
        llm_client: Optional[LLM] = None,
        simulator: Optional[Simulator] = None,
        memory: Optional[Memory] = None,
        economy_client: Optional[EconomyClient] = None,
        messager: Optional[Messager] = None,
        avro_file: Optional[dict] = None,
    ) -> None:
        super().__init__(
            name=name,
            llm_client=llm_client,
            simulator=simulator,
            memory=memory,
            economy_client=economy_client,
            messager=messager,
            avro_file=avro_file,
        )
        self.initailzed = False
        self.last_time_trigger = None
        self.time_diff = 30 * 24 * 60 * 60
        self.forward_times = 0

    async def month_trigger(self):
        now_time = await self.simulator.get_time()
        if self.last_time_trigger is None:
            self.last_time_trigger = now_time
            return False
        if now_time - self.last_time_trigger >= self.time_diff:
            self.last_time_trigger = now_time
            return True
        return False

    async def gather_messages(self, agent_ids, content):
        infos = await super().gather_messages(agent_ids, content)
        return [info["content"] for info in infos]

    async def forward(self):
        if await self.month_trigger():
            print("bank forward")
            interest_rate = await self.economy_client.get(self._agent_id, 'interest_rate')
            citizens = await self.economy_client.get(self._agent_id, 'citizens')
            for citizen in citizens:
                wealth = await self.economy_client.get(citizen, 'currency')
                await self.economy_client.add_delta_value(citizen, 'currency', interest_rate*wealth)
            nbs_id = await self.economy_client.get_org_entity_ids(economyv2.ORG_TYPE_NBS)
            nbs_id = nbs_id[0]
            prices = await self.economy_client.get(nbs_id, 'prices')
            inflations = calculate_inflation(prices)
            natural_interest_rate = 0.01
            target_inflation = 0.02
            if len(inflations) > 0:
                # natural_unemployment_rate = 0.04
                inflation_coeff, unemployment_coeff = 0.5, 0.5
                tao = 1
                avg_inflation = np.mean(inflations[-tao:])
                interest_rate = natural_interest_rate + target_inflation + inflation_coeff * (avg_inflation - target_inflation)
            else:
                interest_rate = natural_interest_rate + target_inflation
            await self.economy_client.update(self._agent_id, 'interest_rate', interest_rate)
            print("bank forward end")
