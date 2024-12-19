from dataclasses import dataclass, field
from typing import List, Dict, Optional
from datetime import datetime
from enum import Enum
import uuid


class QuestionType(Enum):
    TEXT = "文本"
    SINGLE_CHOICE = "单选"
    MULTIPLE_CHOICE = "多选"
    RATING = "评分"
    LIKERT = "李克特量表"


@dataclass
class Question:
    content: str
    type: QuestionType
    required: bool = True
    options: List[str] = field(default_factory=list)
    min_rating: int = 1
    max_rating: int = 5

    def to_dict(self) -> dict:
        return {
            "content": self.content,
            "type": self.type.value,
            "required": self.required,
            "options": self.options,
            "min_rating": self.min_rating,
            "max_rating": self.max_rating,
        }


@dataclass
class Survey:
    id: str
    title: str
    description: str
    questions: List[Question]
    responses: Dict[str, dict] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "questions": [q.to_dict() for q in self.questions],
            "response_count": len(self.responses),
        }
