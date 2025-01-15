import asyncio
from typing import Optional

import numpy as np
from pycityagent import Simulator, InstitutionAgent
from pycityagent.llm.llm import LLM
from pycityagent.economy import EconomyClient
from pycityagent.message import Messager
from pycityagent.memory import Memory
import logging

logger = logging.getLogger("pycityagent")


class FirmAgent(InstitutionAgent):
    configurable_fields = ["time_diff", "max_price_inflation", "max_wage_inflation"]
    default_values = {
        "time_diff": 30 * 24 * 60 * 60,
        "max_price_inflation": 0.05,
        "max_wage_inflation": 0.05,
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
            employees = await self.memory.status.get("employees")
            agents_forward = []
            if not np.all(np.array(agents_forward) > self.forward_times):
                return
            goods_demand = await self.gather_messages(employees, "goods_demand")
            goods_consumption = await self.gather_messages(
                employees, "goods_consumption"
            )
            print(
                f"goods_demand: {goods_demand}, goods_consumption: {goods_consumption}"
            )
            total_demand = sum(goods_demand)
            last_inventory = sum(goods_consumption) + await self.economy_client.get(
                self._agent_id, "inventory"
            )
            print(
                f"total_demand: {total_demand}, last_inventory: {last_inventory}, goods_contumption: {sum(goods_consumption)}"
            )
            max_change_rate = (total_demand - last_inventory) / (
                max(total_demand, last_inventory) + 1e-8
            )
            skills = await self.gather_messages(employees, "work_skill")
            for skill, uuid in zip(skills, employees):
                await self.send_message_to_agent(
                    uuid,
                    f"work_skill@{max(skill*(1 + np.random.uniform(0, max_change_rate*self.max_wage_inflation)), 1)}",
                    "economy",
                )
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
            self.forward_times += 1
            for uuid in employees:
                await self.send_message_to_agent(
                    uuid, f"firm_forward@{self.forward_times}", "economy"
                )
