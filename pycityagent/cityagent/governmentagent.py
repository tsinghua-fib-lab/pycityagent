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


class GovernmentAgent(InstitutionAgent):
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
            citizens = await self.memory.get("citizens")
            while True:
                agents_forward = await self.gather_messages(citizens, "forward")
                if np.all(np.array(agents_forward) > self.forward_times):
                    break
                await asyncio.sleep(1)
            citizens_agent_id = await self.memory.get("citizens_agent_id")
            incomes = await self.gather_messages(citizens, "income_currency")  # uuid
            _, post_tax_incomes = await self.economy_client.calculate_taxes_due(
                self._agent_id, citizens_agent_id, incomes, enable_redistribution=False
            )
            for uuid, income, post_tax_income in zip(
                citizens, incomes, post_tax_incomes
            ):
                tax_paid = income - post_tax_income
                await self.send_message_to_agent(uuid, f"tax_paid@{tax_paid}")
            self.forward_times += 1
            for uuid in citizens:
                await self.send_message_to_agent(
                    uuid, f"government_forward@{self.forward_times}"
                )
