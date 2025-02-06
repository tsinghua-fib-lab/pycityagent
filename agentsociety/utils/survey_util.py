def process_survey_for_llm(survey_dict: dict) -> str:
    """
    将问卷字典转换为LLM可以逐题处理的格式，使用英文提示
    """
    prompt = f"""Survey Title: {survey_dict['title']}
Survey Description: {survey_dict['description']}

Please answer each question in the following format:

"""

    question_count = 1
    for page in survey_dict["pages"]:
        for question in page["elements"]:
            prompt += f"Question {question_count}: {question['title']}\n"

            # 根据不同类型的问题生成不同的提示
            if question["type"] == "radiogroup":
                prompt += "Options: " + ", ".join(question["choices"]) + "\n"
                prompt += "Please select ONE option\n"

            elif question["type"] == "checkbox":
                prompt += "Options: " + ", ".join(question["choices"]) + "\n"
                prompt += "You can select MULTIPLE options\n"

            elif question["type"] == "rating":
                prompt += f"Rating range: {question.get('min_rating', 1)} - {question.get('max_rating', 5)}\n"
                prompt += "Please provide a rating within the range\n"

            elif question["type"] == "matrix":
                prompt += "Rows: " + ", ".join(question["rows"]) + "\n"
                prompt += "Columns: " + ", ".join(question["columns"]) + "\n"
                prompt += "Please select ONE column option for EACH row\n"

            elif question["type"] == "text":
                prompt += "Please provide a text response\n"

            elif question["type"] == "boolean":
                prompt += "Options: Yes, No\n"
                prompt += "Please select either Yes or No\n"

            prompt += "\nAnswer: [Your response here]\n\n---\n\n"
            question_count += 1

    # 添加总结提示
    prompt += """Please ensure:
1. All required questions are answered
2. Responses match the question type requirements
3. Answers are clear and specific

Format your responses exactly as requested above."""

    return prompt


SURVEY_SENDER_UUID = "none"
