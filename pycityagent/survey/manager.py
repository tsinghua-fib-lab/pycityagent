import json
import uuid
from datetime import datetime
from typing import Optional

from .models import Page, Question, QuestionType, Survey


class SurveyManager:
    def __init__(self):
        self._surveys: dict[str, Survey] = {}

    def create_survey(self, title: str, description: str, pages: list[dict]) -> Survey:
        """创建新问卷"""
        survey_id = uuid.uuid4()

        # 转换页面和问题数据
        survey_pages = []
        for page_data in pages:
            questions = []
            for q in page_data["elements"]:
                question = Question(
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
                questions.append(question)

            page = Page(name=page_data["name"], elements=questions)
            survey_pages.append(page)

        survey = Survey(
            id=survey_id,
            title=title,
            description=description,
            pages=survey_pages,
        )

        self._surveys[str(survey_id)] = survey
        return survey

    def get_survey(self, survey_id: str) -> Optional[Survey]:
        """获取指定问卷"""
        return self._surveys.get(survey_id)

    def get_all_surveys(self) -> list[Survey]:
        """获取所有问卷"""
        return list(self._surveys.values())
