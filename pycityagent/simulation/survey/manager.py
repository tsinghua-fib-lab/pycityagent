from typing import List, Dict, Optional
from datetime import datetime
import uuid
import json
from .models import Survey, Question, QuestionType


class SurveyManager:
    def __init__(self):
        self._surveys: Dict[str, Survey] = {}

    def create_survey(
        self, title: str, description: str, questions: List[dict]
    ) -> Survey:
        """创建新问卷"""
        survey_id = str(uuid.uuid4())

        # 转换问题数据
        survey_questions = []
        for q in questions:
            question = Question(
                content=q["content"],
                type=QuestionType(q["type"]),
                required=q.get("required", True),
                options=q.get("options", []),
                min_rating=q.get("min_rating", 1),
                max_rating=q.get("max_rating", 5),
            )
            survey_questions.append(question)

        survey = Survey(
            id=survey_id,
            title=title,
            description=description,
            questions=survey_questions,
        )

        self._surveys[survey_id] = survey
        return survey

    def get_survey(self, survey_id: str) -> Optional[Survey]:
        """获取指定问卷"""
        return self._surveys.get(survey_id)

    def get_all_surveys(self) -> List[Survey]:
        """获取所有问卷"""
        return list(self._surveys.values())

    def add_response(self, survey_id: str, agent_name: str, response: dict) -> bool:
        """添加问卷回答"""
        survey = self.get_survey(survey_id)
        if not survey:
            return False

        survey.responses[agent_name] = {"timestamp": datetime.now(), **response}
        return True

    def export_results(self, survey_id: str) -> str:
        """导出问卷结果"""
        survey = self.get_survey(survey_id)
        if not survey:
            return json.dumps({"error": "问卷不存在"})

        return json.dumps(
            {"survey": survey.to_dict(), "responses": survey.responses},
            ensure_ascii=False,
            indent=2,
        )
