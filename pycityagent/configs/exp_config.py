from __future__ import annotations

import logging
from collections.abc import Callable
from typing import TYPE_CHECKING, Any, Literal, Optional, Union

from pydantic import BaseModel, Field

from ..utils import WorkflowType

if TYPE_CHECKING:
    from ..simulation import AgentSimulation


class WorkflowStep(BaseModel):
    type: WorkflowType
    days: int = Field(1, description="Number of simulation days")
    times: int = Field(1, description="Step Execution Times")
    description: str = Field("no description")
    func: Optional[Callable] = None


class AgentConfig(BaseModel):

    number_of_citizen: int = Field(1, description="Number of citizens")
    number_of_firm: int = Field(1, description="Number of firms")
    number_of_government: int = Field(1, description="Number of governments")
    number_of_bank: int = Field(1, description="Number of banks")
    number_of_nbs: int = Field(1, description="Number of neighborhood-based services")
    group_size: int = Field(100, description="Size of agent groups")
    embedding_model: Any = Field(None, description="Embedding model")
    agent_class_configs: Optional[dict[Any, dict[str, Any]]] = None
    memory_config_func: Optional[dict[type["Any"], Callable]] = None
    memory_config_init_func: Optional[Callable] = Field(None)
    init_func: Optional[list[Callable[["AgentSimulation"], None]]] = None
    enable_institution: bool = Field(
        True, description="Whether institutions are enabled in the experiment"
    )

    @classmethod
    def create(
        cls,
        number_of_citizen: int = 1,
        number_of_firm: int = 1,
        number_of_government: int = 1,
        number_of_bank: int = 1,
        number_of_nbs: int = 1,
        group_size: int = 100,
        embedding_model: Any = None,
        agent_class_configs: Optional[dict[Any, dict[str, Any]]] = None,
        enable_institution: bool = True,
        memory_config_func: Optional[dict[type["Any"], Callable]] = None,
        memory_config_init_func: Optional[Callable] = None,
        init_func: Optional[list[Callable[["AgentSimulation"], None]]] = None,
    ) -> "AgentConfig":
        return cls(
            number_of_citizen=number_of_citizen,
            number_of_firm=number_of_firm,
            number_of_government=number_of_government,
            number_of_bank=number_of_bank,
            number_of_nbs=number_of_nbs,
            group_size=group_size,
            embedding_model=embedding_model,
            agent_class_configs=agent_class_configs,
            enable_institution=enable_institution,
            memory_config_func=memory_config_func,
            memory_config_init_func=memory_config_init_func,
            init_func=init_func,
        )


class EnvironmentConfig(BaseModel):
    weather: str = Field(default="The weather is normal")
    crime: str = Field(default="The crime rate is low")
    pollution: str = Field(default="The pollution level is low")
    temperature: str = Field(default="The temperature is normal")
    day: str = Field(default="Workday")

    @classmethod
    def create(
        cls,
        weather: str = "The weather is normal",
        crime: str = "The crime rate is low",
        pollution: str = "The pollution level is low",
        temperature: str = "The temperature is normal",
        day: str = "Workday",
    ) -> "EnvironmentConfig":
        return cls(
            weather=weather,
            crime=crime,
            pollution=pollution,
            temperature=temperature,
            day=day,
        )


class MessageInterceptConfig(BaseModel):
    mode: str = Field(..., pattern="^(point|edge)$")
    max_violation_time: int = Field(default=3)

    @classmethod
    def create(cls, mode: str, max_violation_time: int = 3) -> "MessageInterceptConfig":
        return cls(mode=mode, max_violation_time=max_violation_time)


class ExpConfig(BaseModel):
    agent_config: Optional[AgentConfig] = None
    workflow: Optional[list[WorkflowStep]] = None
    environment: Optional[EnvironmentConfig] = EnvironmentConfig()
    message_intercept: Optional[MessageInterceptConfig] = None
    metric_extractors: Optional[list[tuple[int, Callable]]] = None
    logging_level: int = Field(logging.WARNING)
    exp_name: str = Field("default_experiment")
    llm_semaphore: int = Field(200)

    @property
    def prop_agent_config(self) -> AgentConfig:
        return self.agent_config  # type:ignore

    @property
    def prop_workflow(self) -> list[WorkflowStep]:
        return self.workflow  # type:ignore

    @property
    def prop_environment(self) -> EnvironmentConfig:
        return self.environment  # type:ignore

    @property
    def prop_message_intercept(self) -> MessageInterceptConfig:
        return self.message_intercept  # type:ignore

    @property
    def prop_metric_extractors(
        self,
    ) -> list[tuple[int, Callable]]:
        return self.metric_extractors  # type:ignore

    def SetAgentConfig(
        self,
        number_of_citizen: int = 1,
        number_of_firm: int = 1,
        number_of_government: int = 1,
        number_of_bank: int = 1,
        number_of_nbs: int = 1,
        group_size: int = 100,
        embedding_model: Any = None,
        agent_class_configs: Optional[dict[Any, dict[str, list[dict]]]] = None,
        enable_institution: bool = True,
        memory_config_func: Optional[dict[type["Any"], Callable]] = None,
        memory_config_init_func: Optional[Callable] = None,
        init_func: Optional[list[Callable[["AgentSimulation"], None]]] = None,
    ) -> "ExpConfig":
        self.agent_config = AgentConfig.create(
            number_of_citizen=number_of_citizen,
            number_of_firm=number_of_firm,
            number_of_government=number_of_government,
            number_of_bank=number_of_bank,
            number_of_nbs=number_of_nbs,
            group_size=group_size,
            embedding_model=embedding_model,
            agent_class_configs=agent_class_configs,
            enable_institution=enable_institution,
            memory_config_func=memory_config_func,
            memory_config_init_func=memory_config_init_func,
            init_func=init_func,
        )
        return self

    def SetEnvironment(
        self,
        weather: str = "The weather is normal",
        crime: str = "The crime rate is low",
        pollution: str = "The pollution level is low",
        temperature: str = "The temperature is normal",
        day: str = "Workday",
    ) -> "ExpConfig":
        self.environment = EnvironmentConfig.create(
            weather=weather,
            crime=crime,
            pollution=pollution,
            temperature=temperature,
            day=day,
        )
        return self

    def SetMessageIntercept(
        self,
        mode: Union[Literal["point"], Literal["edge"]],
        max_violation_time: int = 3,
    ) -> "ExpConfig":
        self.message_intercept = MessageInterceptConfig.create(
            mode=mode, max_violation_time=max_violation_time
        )
        return self

    def SetMetricExtractors(self, metric_extractors: list[tuple[int, Callable]]):
        self.metric_extractors = metric_extractors
        return self

    def SetWorkFlow(self, workflows: list[WorkflowStep]):
        self.workflow = workflows
        return self
