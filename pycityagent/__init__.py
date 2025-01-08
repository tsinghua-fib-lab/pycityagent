"""
Pycityagent: 城市智能体构建框架
"""

import logging

from .agent import Agent, AgentType, CitizenAgent, InstitutionAgent
from .environment import Simulator
from .llm import SentenceEmbedding
from .simulation import AgentSimulation

# 创建一个 pycityagent 记录器
logger = logging.getLogger("pycityagent")
logger.setLevel(logging.WARNING)  # 默认级别

# 如果没有处理器，则添加一个
if not logger.hasHandlers():
    handler = logging.StreamHandler()
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)

__all__ = [
    "Agent",
    "Simulator",
    "CitizenAgent",
    "InstitutionAgent",
    "SentenceEmbedding",
    "AgentSimulation",
    "AgentType",
]
