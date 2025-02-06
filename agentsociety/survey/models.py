import json
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any


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
    choices: list[str] = field(default_factory=list)
    columns: list[str] = field(default_factory=list)
    rows: list[str] = field(default_factory=list)
    required: bool = True
    min_rating: int = 1
    max_rating: int = 5

    def to_dict(self) -> dict:
        base_dict: dict[str, Any] = {
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
    elements: list[Question]

    def to_dict(self) -> dict:
        return {"name": self.name, "elements": [q.to_dict() for q in self.elements]}


@dataclass
class Survey:
    """
    Represents a survey with metadata and associated pages containing questions.

    - **Attributes**:
        - `id` (uuid.UUID): Unique identifier for the survey.
        - `title` (str): Title of the survey.
        - `description` (str): Description of the survey's purpose or content.
        - `pages` (list[Page]): A list of `Page` objects, each containing a set of questions.
        - `responses` (dict[str, dict], optional): Dictionary mapping response IDs to their data. Defaults to an empty dictionary.
        - `created_at` (datetime, optional): Timestamp of when the survey was created. Defaults to the current time.
    """

    id: uuid.UUID
    title: str
    description: str
    pages: list[Page]
    responses: dict[str, dict] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> dict:
        """
        Convert the survey instance into a dictionary representation.

        - **Description**:
            - Creates a dictionary containing the survey's ID, title, description, and pages in a simplified format suitable for serialization.

        - **Returns**:
            - `dict`: Simplified dictionary representation of the survey.
        """
        return {
            "id": str(self.id),
            "title": self.title,
            "description": self.description,
            "pages": [p.to_dict() for p in self.pages],
            "response_count": len(self.responses),
        }

    def to_json(self) -> str:
        """
        Serialize the survey instance to a JSON string for MQTT transmission.

        - **Description**:
            - Converts the survey into a JSON string that includes all necessary information for reconstructing the survey object on another system.

        - **Returns**:
            - `str`: JSON string representing the survey.
        """
        survey_dict = {
            "id": str(self.id),
            "title": self.title,
            "description": self.description,
            "pages": [p.to_dict() for p in self.pages],
            "responses": self.responses,
            "created_at": self.created_at.isoformat(),
        }
        return json.dumps(survey_dict)

    @classmethod
    def from_json(cls, json_str: str) -> "Survey":
        """
        Deserialize a JSON string into a new Survey instance.

        - **Description**:
            - Parses a JSON string into a Python dictionary and uses it to create a new `Survey` instance.

        - **Args**:
            - `json_str` (str): JSON string representation of a survey.

        - **Returns**:
            - `Survey`: An instance of `Survey` initialized with the data from the JSON string.
        """
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
                        max_rating=q.get("max_rating", 5),
                    )
                    for q in p["elements"]
                ],
            )
            for p in data["pages"]
        ]

        return cls(
            id=uuid.UUID(data["id"]),
            title=data["title"],
            description=data["description"],
            pages=pages,
            responses=data.get("responses", {}),
            created_at=datetime.fromisoformat(data["created_at"]),
        )
