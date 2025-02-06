import asyncio
import logging
from typing import Optional

import numpy as np

from agentsociety import InstitutionAgent, Simulator
from agentsociety.environment import EconomyClient
from agentsociety.llm.llm import LLM
from agentsociety.memory import Memory
from agentsociety.message import Messager
import pycityproto.city.economy.v2.economy_pb2 as economyv2

logger = logging.getLogger("agentsociety")


class NBSAgent(InstitutionAgent):
    configurable_fields = ["time_diff", "num_labor_hours", "productivity_per_labor"]
    default_values = {
        "time_diff": 30 * 24 * 60 * 60,
        "num_labor_hours": 168,
        "productivity_per_labor": 1,
    }
    fields_description = {
        "time_diff": "Time difference between each forward, day * hour * minute * second",
        "num_labor_hours": "Number of labor hours per week",
        "productivity_per_labor": "Productivity per labor hour",
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
            print("nbs forward")
            await self.economy_client.calculate_real_gdp(self._agent_id)
            citizens_uuid = await self.memory.status.get("citizens")
            citizens = await self.economy_client.get(self._agent_id, "citizens")
            work_propensity = await self.gather_messages(citizens_uuid, "work_propensity")
            if sum(work_propensity) == 0.0:
                working_hours = 0.0
            else:
                working_hours = np.mean(work_propensity) * self.num_labor_hours
            await self.economy_client.update(
                self._agent_id, "working_hours", [working_hours], mode="merge"
            )
            firms_id = await self.economy_client.get_org_entity_ids(economyv2.ORG_TYPE_FIRM)
            prices = await self.economy_client.get(firms_id, "price")

            await self.economy_client.update(
                self._agent_id, "prices", [float(np.mean(prices))], mode="merge"
            )
            depression = await self.gather_messages(citizens_uuid, "depression")
            if sum(depression) == 0.0:
                depression = 0.0
            else:
                depression = np.mean(depression)
            await self.economy_client.update(
                self._agent_id, "depression", [depression], mode="merge"
            )
            consumption_currency = await self.economy_client.get(citizens, "consumption")
            if sum(consumption_currency) == 0.0:
                consumption_currency = 0.0
            else:
                consumption_currency = np.mean(consumption_currency)
            await self.economy_client.update(
                self._agent_id,
                "consumption_currency",
                [consumption_currency],
                mode="merge",
            )
            income_currency = await self.economy_client.get(citizens, "income")
            if sum(income_currency) == 0.0:
                income_currency = 0.0
            else:
                income_currency = np.mean(income_currency)
            await self.economy_client.update(
                self._agent_id, "income_currency", [income_currency], mode="merge"
            )
            print("nbs forward end")
            self.forward_times += 1
            await self.memory.status.update("forward_times", self.forward_times)
