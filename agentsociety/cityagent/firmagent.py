from typing import Optional

import numpy as np
from agentsociety import Simulator, InstitutionAgent
from agentsociety.llm import LLM
from agentsociety.environment import EconomyClient
from agentsociety.message import Messager
from agentsociety.memory import Memory
import logging

logger = logging.getLogger("agentsociety")


class FirmAgent(InstitutionAgent):
    configurable_fields = ["time_diff", "max_price_inflation", "max_wage_inflation"]
    default_values = {
        "time_diff": 30 * 24 * 60 * 60,
        "max_price_inflation": 0.05,
        "max_wage_inflation": 0.05,
    }
    fields_description = {
        "time_diff": "Time difference between each forward, day * hour * minute * second",
        "max_price_inflation": "Maximum price inflation rate",
        "max_wage_inflation": "Maximum wage inflation rate",
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
        self.forward_times = 0
        self.time_diff = 30 * 24 * 60 * 60
        self.max_price_inflation = 0.05
        self.max_wage_inflation = 0.05

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
            print("firm forward")
            employees = await self.economy_client.get(self._agent_id, "employees")
            total_demand = await self.economy_client.get(self._agent_id, "demand")
            goods_consumption = await self.economy_client.get(self._agent_id, "sales")
            last_inventory = goods_consumption + await self.economy_client.get(self._agent_id, "inventory")
            max_change_rate = (total_demand - last_inventory) / (max(total_demand, last_inventory) + 1e-8)
            skills = await self.economy_client.get(employees, "skill")
            skills = np.array(skills)
            skill_change_ratio = np.random.uniform(0, max_change_rate*self.max_wage_inflation)
            await self.economy_client.update(employees, "skill", list(np.maximum(skills*(1 + skill_change_ratio), 1)))
            price = await self.economy_client.get(self._agent_id, "price")
            await self.economy_client.update(
                self._agent_id,
                "price",
                max(
                    price
                    * (
                        1
                        + np.random.uniform(
                            0, max_change_rate * self.max_price_inflation
                        )
                    ),
                    1,
                ),
            )
            await self.economy_client.update(self._agent_id, 'demand', 0)
            await self.economy_client.update(self._agent_id, 'sales', 0)
            print("firm forward end")
