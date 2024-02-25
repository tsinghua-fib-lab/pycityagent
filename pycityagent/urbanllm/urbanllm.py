from openai import OpenAI
from http import HTTPStatus
import dashscope
from urllib.parse import urlparse, unquote
from pathlib import PurePosixPath
import requests
from dashscope import ImageSynthesis
from PIL import Image
from io import BytesIO

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
        self.image_u = config['img_understand_request']
        self.image_g = config['img_generate_request']

class UrbanLLM:
    """
    大语言模型对象
    The LLM Object used by Agent(Soul)
    """
    def __init__(self, config: LLMConfig) -> None:
        self.config = config

    def text_request(self, dialog:list[dict]) -> str:
        """
        文本相关请求
        Text request

        Args:
        - dialog (list[dict]): 标准的LLM文本dialog. The standard text LLM dialog

        Returns:
        - (str): the response content
        """
        if self.config.text['request_type'] == 'openai':
            client = OpenAI(
                api_key=self.config.text['api_key'], 
                base_url=self.config.text['api_base']
            )
            response = client.chat.completions.create(
                model=self.config.text['model'],
                messages=dialog,
                temperature=1.0,
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
                return "Error: {}".format(response.status_code)
        else:
            print("ERROR: Wrong Config")
            return "wrong config"

    def img_understand(self, img_path:str, prompt:str=None) -> str:
        """
        图像理解
        Image understanding

        Args:
        - img_path: 图像的绝对路径. The absolute path of selected Image
        - prompt: 理解提示词 - 例如理解方向. The understanding prompts

        Returns:
        - (str): the understanding content
        """
        ppt = "如何理解这幅图像？"
        if prompt != None:
            ppt += prompt
        dialog = [{
            'role': 'user',
            'content': [
                {'image': 'file://' + img_path},
                {'text': ppt}
            ]
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

    def img_generate(self, prompt, size:str='512*512', quantity:int = 1):
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