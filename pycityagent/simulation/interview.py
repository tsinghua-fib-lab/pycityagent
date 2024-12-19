from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional


@dataclass
class InterviewRecord:
    """采访记录"""

    timestamp: datetime
    agent_name: str
    question: str
    response: str
    blocking: bool


class InterviewManager:
    """采访管理器"""

    def __init__(self):
        self._history: List[InterviewRecord] = []

    def add_record(self, agent_name: str, question: str, response: str, blocking: bool):
        """添加采访记录"""
        record = InterviewRecord(
            timestamp=datetime.now(),
            agent_name=agent_name,
            question=question,
            response=response,
            blocking=blocking,
        )
        self._history.append(record)

    def get_agent_history(self, agent_name: str) -> List[InterviewRecord]:
        """获取指定智能体的采访历史"""
        return [r for r in self._history if r.agent_name == agent_name]

    def get_recent_history(self, limit: int = 10) -> List[InterviewRecord]:
        """获取最近的采访记录"""
        return sorted(self._history, key=lambda x: x.timestamp, reverse=True)[:limit]
