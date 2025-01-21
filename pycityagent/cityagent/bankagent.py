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

class BankAgent(InstitutionAgent):
    def __init__(
        self,
        name: str,
        llm_client: Optional[LLM] = None,
        simulator: Optional[Simulator] = None,
        memory: Optional[Memory] = None,
        economy_client: Optional[EconomyClient] = None,
        messager: Optional[Messager] = None,  # type:ignore
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
        now_time: int = await self.simulator.get_time()  # type:ignore
        if self.last_time_trigger is None:
            self.last_time_trigger = now_time
            return False
        if now_time - self.last_time_trigger >= self.time_diff:
            self.last_time_trigger = now_time
            return True
        return False

    async def gather_messages(self, agent_ids, content):  # type:ignore
        infos = await super().gather_messages(agent_ids, content)
        return [info["content"] for info in infos]

    async def forward(self):
        if await self.month_trigger():
            citizens = await self.memory.status.get("citizens")
            agents_forward = []
            if not np.all(np.array(agents_forward) > self.forward_times):
                return
            self.forward_times += 1
            for uuid in citizens:
                await self.send_message_to_agent(
                    uuid, f"bank_forward@{self.forward_times}", "economy"
                )
