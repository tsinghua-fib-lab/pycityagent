from dataclasses import dataclass, field
from typing import List, Dict, Optional
from datetime import datetime
from enum import Enum
import uuid
import json


class QuestionType(Enum):
    TEXT = "text"
    RADIO = "radiogroup"
    CHECKBOX = "checkbox"
    BOOLEAN = "boolean"
    RATING = "rating"
    MATRIX = "matrix"


@dataclass
class Question:
    name: str
    title: str
    type: QuestionType
    choices: List[str] = field(default_factory=list)
    columns: List[str] = field(default_factory=list)
    rows: List[str] = field(default_factory=list)
    min_rating: int = 1
    max_rating: int = 5

    def to_dict(self) -> dict:
        base_dict = {
            "type": self.type.value,
            "name": self.name,
            "title": self.title,
        }
        
        if self.type in [QuestionType.RADIO, QuestionType.CHECKBOX]:
            base_dict["choices"] = self.choices
        elif self.type == QuestionType.MATRIX:
            base_dict["columns"] = self.columns
            base_dict["rows"] = self.rows
        elif self.type == QuestionType.RATING:
            base_dict["min_rating"] = self.min_rating
            base_dict["max_rating"] = self.max_rating
            
        return base_dict


@dataclass
class Page:
    name: str
    elements: List[Question]

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "elements": [q.to_dict() for q in self.elements]
        }


@dataclass
class Survey:
    id: uuid.UUID
    title: str
    description: str
    pages: List[Page]
    responses: Dict[str, dict] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> dict:
        return {
            "id": str(self.id),
            "title": self.title,
            "description": self.description,
            "pages": [p.to_dict() for p in self.pages],
            "response_count": len(self.responses),
        }

    def to_json(self) -> str:
        """Convert the survey to a JSON string for MQTT transmission"""
        survey_dict = {
            "id": str(self.id),
            "title": self.title,
            "description": self.description,
            "pages": [p.to_dict() for p in self.pages],
            "responses": self.responses,
            "created_at": self.created_at.isoformat()
        }
        return json.dumps(survey_dict)

    @classmethod
    def from_json(cls, json_str: str) -> 'Survey':
        """Create a Survey instance from a JSON string"""
        data = json.loads(json_str)
        pages = [
            Page(
                name=p["name"],
                elements=[
                    Question(
                        name=q["name"],
                        title=q["title"],
                        type=QuestionType(q["type"]),
                        required=q.get("required", True),
                        choices=q.get("choices", []),
                        columns=q.get("columns", []),
                        rows=q.get("rows", []),
                        min_rating=q.get("min_rating", 1),
                        max_rating=q.get("max_rating", 5)
                    ) for q in p["elements"]
                ]
            ) for p in data["pages"]
        ]
        
        return cls(
            id=uuid.UUID(data["id"]),
            title=data["title"],
            description=data["description"],
            pages=pages,
            responses=data.get("responses", {}),
            created_at=datetime.fromisoformat(data["created_at"])
        )
