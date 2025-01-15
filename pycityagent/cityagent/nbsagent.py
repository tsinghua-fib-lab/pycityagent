import asyncio
import logging
from typing import Optional

import numpy as np

from pycityagent import InstitutionAgent, Simulator
from pycityagent.economy import EconomyClient
from pycityagent.llm.llm import LLM
from pycityagent.memory import Memory
from pycityagent.message import Messager

logger = logging.getLogger("pycityagent")


class NBSAgent(InstitutionAgent):
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
        self.num_labor_hours = 168
        self.productivity_per_labor = 1
        self.price = 1

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
            citizens = await self.memory.status.get("citizens")
            agents_forward = []
            if not np.all(np.array(agents_forward) > self.forward_times):
                return
            work_propensity = await self.gather_messages(citizens, "work_propensity")
            working_hours = np.mean(work_propensity) * self.num_labor_hours
            firm_id = await self.memory.status.get("firm_id")
            price = await self.economy_client.get(firm_id, "price")
            prices = await self.economy_client.get(self._agent_id, "prices")
            initial_price = prices[0]
            nominal_gdp = (
                working_hours * len(citizens) * self.productivity_per_labor * price
            )
            real_gdp = (
                working_hours
                * len(citizens)
                * self.productivity_per_labor
                * initial_price
            )
            await self.economy_client.update(
                self._agent_id, "nominal_gdp", [nominal_gdp], mode="merge"
            )
            await self.economy_client.update(
                self._agent_id, "real_gdp", [real_gdp], mode="merge"
            )
            await self.economy_client.update(
                self._agent_id, "working_hours", [working_hours], mode="merge"
            )
            await self.economy_client.update(
                self._agent_id, "prices", [price], mode="merge"
            )
            depression = await self.gather_messages(citizens, "depression")
            depression = np.mean(depression)
            await self.economy_client.update(
                self._agent_id, "depression", [depression], mode="merge"
            )
            consumption_currency = await self.gather_messages(
                citizens, "consumption_currency"
            )
            consumption_currency = np.mean(consumption_currency)
            await self.economy_client.update(
                self._agent_id,
                "consumption_currency",
                [consumption_currency],
                mode="merge",
            )
            income_currency = await self.gather_messages(citizens, "income_currency")
            income_currency = np.mean(income_currency)
            await self.economy_client.update(
                self._agent_id, "income_currency", [income_currency], mode="merge"
            )
            self.forward_times += 1
            for uuid in citizens:
                await self.send_message_to_agent(
                    uuid, f"nbs_forward@{self.forward_times}", "economy"
                )
