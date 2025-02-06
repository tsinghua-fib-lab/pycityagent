import uuid
from typing import Optional

from .models import Page, Question, QuestionType, Survey


class SurveyManager:
    def __init__(self):
        """
        Initializes a new instance of the SurveyManager class.

        - **Description**:
            - Manages the creation and retrieval of surveys. Uses an internal dictionary to store survey instances by their unique identifier.

        - **Attributes**:
            - `_surveys` (dict[str, Survey]): A dictionary mapping survey IDs to `Survey` instances.
        """
        self._surveys: dict[str, Survey] = {}

    def create_survey(self, title: str, description: str, pages: list[dict]) -> Survey:
        """
        Create a new survey with specified title, description, and pages containing questions.

        - **Description**:
            - Generates a unique ID for the survey, converts the provided page and question data into `Page` and `Question` objects,
              and adds the created survey to the internal storage.

        - **Args**:
            - `title` (str): The title of the survey.
            - `description` (str): A brief description of what the survey is about.
            - `pages` (list[dict]): A list of dictionaries where each dictionary contains page information including elements which are question definitions.

        - **Returns**:
            - `Survey`: An instance of the `Survey` class representing the newly created survey.
        """
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
        """
        Retrieve a specific survey by its unique identifier.

        - **Description**:
            - Searches for a survey within the internal storage using the provided survey ID.

        - **Args**:
            - `survey_id` (str): The unique identifier of the survey to retrieve.

        - **Returns**:
            - `Optional[Survey]`: An instance of the `Survey` class if found; otherwise, None.
        """
        return self._surveys.get(survey_id)

    def get_all_surveys(self) -> list[Survey]:
        """
        Get all surveys that have been created.

        - **Description**:
            - Retrieves all stored surveys from the internal storage.

        - **Returns**:
            - `list[Survey]`: A list of `Survey` instances.
        """
        return list(self._surveys.values())
