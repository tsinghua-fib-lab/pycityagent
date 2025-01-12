import re
import ast

TIME_ESTIMATE_PROMPT = """As an intelligent agent's time estimation system, please estimate the time needed to complete the current action based on the overall plan and current intention.

Overall plan:
{plan}

Current action: {intention}

Examples:
- "Learn programming": {{"time": 120}}
- "Watch a movie": {{"time": 150}} 
- "Play mobile games": {{"time": 60}}
- "Read a book": {{"time": 90}}
- "Exercise": {{"time": 45}}

Please return the result in JSON format (Do not return any other text):
{{
    "time": estimated completion time (integer, in minutes)
}}
"""

num_labor_hours = 168
month_days = 0.03
productivity_per_labor = 1
max_price_inflation = 0.1
max_wage_inflation = 0.05
natural_interest_rate = 0.01
target_inflation = 0.02
natural_unemployment_rate = 0.04
inflation_coeff, unemployment_coeff = 0.5, 0.5
tao = 1
period = 3
UBI = 0

def prettify_document(document: str) -> str:
    # Remove sequences of whitespace characters (including newlines)
    cleaned = re.sub(r'\s+', ' ', document).strip()
    return cleaned

def extract_dict_from_string(input_string):
    """
    提取输入字符串中的字典。支持跨行字典和嵌套字典。
    """
    # 正则表达式查找所有可能的字典部分，允许多行
    dict_pattern = r'\{(?:[^{}]|\{(?:[^{}]|\{[^{}]*\})*\})*\}'  # 匹配字典的正则表达式，支持嵌套
    matches = re.findall(dict_pattern, input_string, re.DOTALL)  # re.DOTALL允许匹配换行符

    dicts = []

    for match in matches:
        try:
            # 使用 ast.literal_eval 将字符串转换为字典
            parsed_dict = ast.literal_eval(match)
            if isinstance(parsed_dict, dict):
                dicts.append(parsed_dict)
        except (ValueError, SyntaxError) as e:
            print(f"解析字典失败: {e}")

    return dicts

def clean_json_response(response: str) -> str:
    """清理LLM响应中的特殊字符"""
    response = response.replace('```json', '').replace('```', '')
    return response.strip() 
