"""UrbanLLM: 智能能力类及其定义"""

from openai import OpenAI
from http import HTTPStatus
import dashscope
import requests
from dashscope import ImageSynthesis
from PIL import Image
from io import BytesIO
from typing import Union
import base64
import aiohttp

def encode_image(image_path):
  with open(image_path, "rb") as image_file:
    return base64.b64encode(image_file.read()).decode('utf-8')

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
        else:
            print("ERROR: Wrong Config")
            return "wrong config"
        
    async def atext_request(self, dialog:list[dict]):
        """
        异步版文本请求
        目前仅支持qwen模型
        """
        assert self.config.text['request_type'] == 'qwen', "Error: Only support qwen right now"
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