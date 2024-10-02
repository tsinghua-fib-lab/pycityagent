"""UrbanLLM: 智能能力类及其定义"""

from openai import OpenAI, AsyncOpenAI, APIConnectionError, OpenAIError
import openai
import asyncio
from http import HTTPStatus
import dashscope
import requests
from dashscope import ImageSynthesis
from PIL import Image
from io import BytesIO
from typing import Union
import base64
import aiohttp
import re

def encode_image(image_path):
  with open(image_path, "rb") as image_file:
    return base64.b64encode(image_file.read()).decode('utf-8')
  
class VarSet:
    def __init__(self, variable_batch, variable_description, K):
        self.var_batch = variable_batch
        self.var_des = variable_description
        self.var_size = len(list(variable_description.keys()))
        self.batch_size = K
    
    def set_variables(self, variables:list[dict]):
        if len(variables) <= 0 or len(variables) != self.batch_size or (len(variables[0]) != self.var_size):
            print(f"Your input variables mis-match the size of current Variable Set: Batch size-{self.batch_size}, Variable size-{self.var_size}")
            return None
        for i in range(len(self.var_batch)):
            for var, _ in self.var_batch[i].items():
                self.var_batch[i][var] = variables[i][var]

    def get_variables(self):
        return self.var_batch
    
    def get_var_des(self):
        var_des = ""
        for var, desc in self.var_des.items():
            var_des += f"batch[x][{var}] -- {desc}\n"
        return var_des

class PromptBatch:
    def __init__(self, prompt_batch:str, variable_batch, vasriable_description, K):
        self.prompt_raw = prompt_batch
        self.prompt_set = None
        self.batch_size = K
        self.var_set = VarSet(variable_batch, vasriable_description, K)
    
    def set_variables(self, variables:list[dict]):
        self.var_set.set_variables(variables)
        self.prompt_set = self.prompt_raw.format(batch=self.get_variables())

    def get_variables(self):
        return self.var_set.var_batch

    def get_prompt(self):
        if self.prompt_set == None:
            return self.prompt_raw
        return self.prompt_set

class LLMConfig:
    """
    大语言模型相关配置
    The config of LLM
    """
    def __init__(
        self, 
        config: dict
    ) -> None:
        self.config = config
        self.text = config['text_request']
        if 'api_base' in self.text.keys() and self.text['api_base'] == 'None':
            self.text['api_base'] = None
        self.image_u = config['img_understand_request']
        self.image_g = config['img_generate_request']

class UrbanLLM:
    """
    大语言模型对象
    The LLM Object used by Agent(Soul)
    """
    def __init__(self, config: LLMConfig) -> None:
        self.config = config
        self.prompt_tokens_used = 0
        self.completion_tokens_used = 0
        self.request_number = 0
        self.semaphore = None
        self._aclient = AsyncOpenAI(api_key=self.config.text['api_key'], timeout=300)

    def set_semaphore(self, number_of_coroutine:int):
        self.semaphore = asyncio.Semaphore(number_of_coroutine)

    def clear_semaphore(self):
        self.semaphore = None

    def clear_used(self):
        """
        clear the storage of used tokens to start a new log message
        Only support OpenAI category API right now, including OpenAI, Deepseek
        """
        self.prompt_tokens_used = 0
        self.completion_tokens_used = 0
        self.request_number = 0

    def show_consumption(self, input_price:float=None, output_price:float=None):
        """
        if you give the input and output price of using model, this function will also calculate the consumption for you
        """
        total_token = self.prompt_tokens_used + self.completion_tokens_used
        if self.completion_tokens_used != 0:
            rate = self.prompt_tokens_used/self.completion_tokens_used
        else:
            rate = 'nan'
        if self.request_number != 0:
            TcA = total_token/self.request_number
        else:
            TcA = 'nan'
        out = f"""Request Number: {self.request_number}
Token Usage:
    - Total tokens: {total_token}
    - Prompt tokens: {self.prompt_tokens_used}
    - Completion tokens: {self.completion_tokens_used}
    - Token per request: {TcA}
    - Prompt:Completion ratio: {rate}:1"""
        if input_price != None and output_price != None:
            consumption = self.prompt_tokens_used/1000000*input_price + self.completion_tokens_used/1000000*output_price
            out += f"\n    - Cost Estimation: {consumption}"
        print(out)
        return {"total": total_token, "prompt": self.prompt_tokens_used, "completion": self.completion_tokens_used, "ratio": rate}


    def text_request(self, dialog:list[dict], temperature:float=1, max_tokens:int=None, top_p:float=None, frequency_penalty:float=None, presence_penalty:float=None) -> str:
        """
        文本相关请求
        Text request

        Args:
        - dialog (list[dict]): 标准的LLM文本dialog. The standard text LLM dialog
        - temperature (float): default 1, used in openai
        - max_tokens (int): default None, used in openai
        - top_p (float): default None, used in openai
        - frequency_penalty (float): default None, used in openai
        - presence_penalty (float): default None, used in openai

        Returns:
        - (str): the response content
        """
        if 'api_base' in self.config.text.keys():
            api_base = self.config.text['api_base']
        else:
            api_base = None
        if self.config.text['request_type'] == 'openai':
            client = OpenAI(
                api_key=self.config.text['api_key'], 
                base_url=api_base,
            )
            response = client.chat.completions.create(
                model=self.config.text['model'],
                messages=dialog,
                temperature=temperature,
                max_tokens=max_tokens,
                top_p=top_p,
                frequency_penalty=frequency_penalty,
                presence_penalty=presence_penalty
            )
            self.prompt_tokens_used += response.usage.prompt_tokens
            self.completion_tokens_used += response.usage.completion_tokens
            self.request_number += 1
            return response.choices[0].message.content
        elif self.config.text['request_type'] == 'qwen':
            response = dashscope.Generation.call(
                model=self.config.text['model'],
                api_key=self.config.text['api_key'],
                messages=dialog,
                result_format='message'
            )
            if response.status_code == HTTPStatus.OK:
                return response.output.choices[0]['message']['content']
            else:
                return "Error: {}, {}".format(response.status_code, response.message)
        elif self.config.text['request_type'] == 'deepseek':
            client = OpenAI(
                api_key=self.config.text['api_key'],
                base_url="https://api.deepseek.com/beta",
            )
            response = client.chat.completions.create(
                model=self.config.text['model'],
                messages=dialog,
                temperature=temperature,
                max_tokens=max_tokens,
                top_p=top_p,
                frequency_penalty=frequency_penalty,
                presence_penalty=presence_penalty,
                stream=False,
            )
            self.prompt_tokens_used += response.usage.prompt_tokens
            self.completion_tokens_used += response.usage.completion_tokens
            self.request_number += 1
            return response.choices[0].message.content
        else:
            print("ERROR: Wrong Config")
            return "wrong config"
        
    async def atext_request(self, dialog:list[dict], temperature:float=1, max_tokens:int=None, top_p:float=None, frequency_penalty:float=None, presence_penalty:float=None, timeout:int=300, retries=3):
        """
        异步版文本请求
        """
        if self.config.text['request_type'] == 'openai':
            for attempt in range(retries):
                try:
                    if self.semaphore != None:
                        async with self.semaphore:
                            response = await self._aclient.chat.completions.create(
                                model=self.config.text['model'],
                                messages=dialog,
                                temperature=temperature,
                                max_tokens=max_tokens,
                                top_p=top_p,
                                frequency_penalty=frequency_penalty,
                                presence_penalty=presence_penalty,
                                stream=False,
                                timeout=timeout,
                            )
                            self.prompt_tokens_used += response.usage.prompt_tokens
                            self.completion_tokens_used += response.usage.completion_tokens
                            self.request_number += 1
                            return response.choices[0].message.content
                    else:
                        response = await self._aclient.chat.completions.create(
                            model=self.config.text['model'],
                            messages=dialog,
                            temperature=temperature,
                            max_tokens=max_tokens,
                            top_p=top_p,
                            frequency_penalty=frequency_penalty,
                            presence_penalty=presence_penalty,
                            stream=False,
                            timeout=timeout,
                        )
                        self.prompt_tokens_used += response.usage.prompt_tokens
                        self.completion_tokens_used += response.usage.completion_tokens
                        self.request_number += 1
                        return response.choices[0].message.content
                except APIConnectionError as e:
                    print("API connection error:", e)
                    if attempt < retries - 1:
                        await asyncio.sleep(2 ** attempt)
                    else:
                        raise e
                except OpenAIError as e:
                    if hasattr(e, 'http_status'):
                        print(f"HTTP status code: {e.http_status}")
                    else:
                        print("An error occurred:", e)
                    if attempt < retries - 1:
                        await asyncio.sleep(2 ** attempt)
                    else:
                        raise e
        elif self.config.text['request_type'] == 'qwen':
            async with aiohttp.ClientSession() as session:
                api_url = "https://dashscope.aliyuncs.com/api/v1/services/aigc/text-generation/generation"
                headers = {"Content-Type": "application/json", "Authorization": f"{self.config.text['api_key']}"}
                payload = {
                    'model': self.config.text['model'],
                    'input': {
                        'messages': dialog
                    }
                }
                async with session.post(api_url, json=payload, headers=headers) as resp:
                    # 错误检查
                    response_json = await resp.json()
                    if 'code' in response_json.keys():
                        raise Exception(f"Error: {response_json['code']}, {response_json['message']}")
                    else:
                        return response_json['output']['text']
        elif self.config.text['request_type'] == 'deepseek':
            client = AsyncOpenAI(
                api_key=self.config.text['api_key'],
                base_url="https://api.deepseek.com/beta",
            )
            response = await client.chat.completions.create(
                model="deepseek-chat",
                messages=dialog,
                temperature=temperature,
                max_tokens=max_tokens,
                top_p=top_p,
                frequency_penalty=frequency_penalty,
                presence_penalty=presence_penalty,
                stream=False,
                timeout=timeout,
            )
            self.prompt_tokens_used += response.usage.prompt_tokens
            self.completion_tokens_used += response.usage.completion_tokens
            self.request_number += 1
            return response.choices[0].message.content
        else:
            print("ERROR: Wrong Config")
            return "wrong config"
        

    async def img_understand(self, img_path:Union[str, list[str]], prompt:str=None) -> str:
        """
        图像理解
        Image understanding

        Args:
        - img_path (Union[str, list[str]]): 目标图像的路径, 既可以是一个路径也可以是包含多张图片路径的list. The path of selected Image
        - prompt (str): 理解提示词 - 例如理解方向. The understanding prompts

        Returns:
        - (str): the understanding content
        """
        ppt = "如何理解这幅图像？"
        if prompt != None:
            ppt = prompt
        if self.config.image_u['request_type'] == 'openai':
            if 'api_base' in self.config.image_u.keys():
                api_base = self.config.image_u['api_base']
            else:
                api_base = None
            client = OpenAI(
                api_key=self.config.text['api_key'], 
                base_url=api_base,
            )
            content = []
            content.append({'type': 'text', 'text': ppt})
            if isinstance(img_path, str):
                base64_image = encode_image(img_path)
                content.append({
                    'type': 'image_url', 
                    'image_url': {
                            'url': f"data:image/jpeg;base64,{base64_image}"
                        }
                })
            elif isinstance(img_path, list) and all(isinstance(item, str) for item in img_path):
                for item in img_path:
                    base64_image = encode_image(item)
                    content.append({
                        'type': 'image_url',
                        'image_url': {
                            'url': f"data:image/jpeg;base64,{base64_image}"
                        }
                    })
            response = client.chat.completions.create(
                model=self.config.image_u['model'],
                messages=[{
                    'role': 'user',
                    'content': content
                }]
            )
            return response.choices[0].message.content
        elif self.config.image_u['request_type'] == 'qwen':
            content = []
            if isinstance(img_path, str):
                content.append({'image': 'file://' + img_path})
                content.append({'text': ppt})
            elif isinstance(img_path, list) and all(isinstance(item, str) for item in img_path):
                for item in img_path:
                    content.append({
                        'image': 'file://' + item
                    })
                content.append({'text': ppt})

            dialog = [{
                'role': 'user',
                'content': content
            }]
            response = dashscope.MultiModalConversation.call(
                        model=self.config.image_u['model'],
                        api_key=self.config.image_u['api_key'],
                        messages=dialog
                    )
            if response.status_code == HTTPStatus.OK:
                return response.output.choices[0]['message']['content']
            else:
                print(response.code)  # The error code.
                return "Error"
        else:
            print("ERROR: wrong image understanding type, only 'openai' and 'openai' is available")
            return "Error"

    async def img_generate(self, prompt:str, size:str='512*512', quantity:int = 1):
        """
        图像生成
        Image generation

        Args:
        - prompt (str): 图像生成提示词. The image generation prompts
        - size (str): 生成图像尺寸, 默认为'512*512'. The image size, default: '512*512'
        - quantity (int): 生成图像数量, 默认为1. The quantity of generated images, default: 1

        Returns:
        - (list[PIL.Image.Image]): 生成的图像列表. The list of generated Images.
        """
        rsp = ImageSynthesis.call(
                model=self.config.image_g['model'],
                api_key=self.config.image_g['api_key'],
                prompt=prompt,
                n=quantity,
                size=size
        )
        if rsp.status_code == HTTPStatus.OK:
            res = []
            for result in rsp.output.results:
                res.append(Image.open(BytesIO(requests.get(result.url).content)))
            return res
        else:
            print('Failed, status_code: %s, code: %s, message: %s' %
                (rsp.status_code, rsp.code, rsp.message))
            return None

    async def convert_prompt_to_batch(self, prompt_raw, K, type:str="mr"):
        """
        将单个目标的 prompt_raw 转换为适合一次批处理调用的 prompt_batch。
        prompt_raw: 单目标的prompt，包含占位符!<INPUT X>!
        K: 批处理的大小
        type: 批处理prompt类型, 'mr': Multi-request; 'gr': Gather-request
        返回值: prompt_batch 和 variable_batch
        """
        # 分割说明性文本和待格式化的 prompt
        sections = prompt_raw.split("<commentblockmarker>###</commentblockmarker>")
        description_section = sections[0].strip()  # 说明文本部分
        prompt_section = sections[1].strip()  # 待格式化的 prompt

        # 1. 提取变量说明
        variable_info = {}
        variable_lines = re.findall(r"!<INPUT (\d+)>! -- (.+)", description_section)
        for var, desc in variable_lines:
            variable_info[int(var)] = desc.strip()
            
        # 找到所有的占位符，如!<INPUT X>!
        placeholders = re.findall(r"!<INPUT (\d+)>!", prompt_section)
        
        # 构建prompt_batch，使用批次变量占位符，并合并为一个请求
        prompt_batch = ""
        for i in range(K):
            current_prompt = prompt_section
            for ph in placeholders:
                current_prompt = current_prompt.replace(f"!<INPUT {ph}>!", f"{{batch[{i}][{ph}]}}")
            prompt_batch += f"### Request {i + 1} ###\n" + current_prompt + "\n"
        
        # 构建variable_batch，假设每个批次有K个值
        variable_batch = [{int(ph): f"input_{i}_{ph}" for ph in placeholders} for i in range(K)]
        if type == "mr":
            return PromptBatch(prompt_batch, variable_batch, variable_info, K)
        elif type == "gr":
            messages = [{
                "role": "system",
                "content": """
You are given a batch prompt structured in multiple requests and a variable description. Your task is to simplify and aggregate this prompt by removing redundant request headers and combining variables across different requests into a more compact format.

### Instructions:
1. Identify all unique sections in the prompt that appear across different requests. These sections will be aggregated into a single instance.
2. For each variable in the prompt (e.g., `{batch[0][0]}`, `{batch[0][1]}`), group them together across all requests, and present them as a list or in a numbered format.
3. Remove all redundant request headers (e.g., `### Request 1 ###`) and replace them with a single unified block where variables are grouped by their positions.
4. Ensure the output is structured clearly for LLM processing, avoiding unnecessary repetition.
5. Ensure the output only contains the transformed prompt.

Here is an example transformation:
Original prompt:
### Request 1 ###
{batch[0][0]}
In general, Your Lifestyle is as follows: {batch[0][1]}
Today is {batch[0][2]}, your wake up hour:
### Request 2 ###
{batch[1][0]}
In general, Your Lifestyle is as follows: {batch[1][1]}
Today is {batch[1][2]}, your wake up hour:
Variable description:
batch[x][0] -- Identity Stable Set
batch[x][1] -- Lifestyle
batch[x][2] -- Day

Transformed prompt:
Your Identity Stable Set:
1. {batch[0][0]}
2. {batch[1][0]}
Your Lifestyle:
1. {batch[0][1]}
2. {batch[1][1]}
The Day:
1. {batch[0][2]}
2. {batch[1][2]}
Today, your wake up hour is:
""",
                }]
            var_des = ""
            for var, desc in variable_info.items():
                var_des += f"batch[x][{var}] -- {desc}\n"
            user_prompt = f"""Here is the original batch prompt:
{prompt_batch}
The Variable description:
{var_des}
"""
            messages.append({'role': 'user', 'content': user_prompt})
            prompt_batch = await self.atext_request(messages)
            return PromptBatch(prompt_batch, variable_batch, variable_info, K)