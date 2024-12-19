"""UrbanLLM: 智能能力类及其定义"""

import json
from openai import OpenAI, AsyncOpenAI, APIConnectionError, OpenAIError
from zhipuai import ZhipuAI
import logging

logging.getLogger("zhipuai").setLevel(logging.WARNING)

import asyncio
from http import HTTPStatus
import dashscope
import requests
from dashscope import ImageSynthesis
from PIL import Image
from io import BytesIO
from typing import Any, Optional, Union, List, Dict
import aiohttp
from .llmconfig import *
from .utils import *

import os

os.environ["GRPC_VERBOSITY"] = "ERROR"


class LLM:
    """
    大语言模型对象
    The LLM Object used by Agent(Soul)
    """

    def __init__(self, config: LLMConfig) -> None:
        self.config = config
        if config.text["request_type"] not in ["openai", "deepseek", "qwen", "zhipuai"]:
            raise ValueError("Invalid request type for text request")
        self.prompt_tokens_used = 0
        self.completion_tokens_used = 0
        self.request_number = 0
        self.semaphore = None
        if self.config.text["request_type"] == "openai":
            self._aclient = AsyncOpenAI(
                api_key=self.config.text["api_key"], timeout=300
            )
        elif self.config.text["request_type"] == "deepseek":
            self._aclient = AsyncOpenAI(
                api_key=self.config.text["api_key"],
                base_url="https://api.deepseek.com/beta",
                timeout=300,
            )
        elif self.config.text["request_type"] == "zhipuai":
            self._aclient = ZhipuAI(api_key=self.config.text["api_key"], timeout=300)

    def set_semaphore(self, number_of_coroutine: int):
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

    def show_consumption(
        self, input_price: Optional[float] = None, output_price: Optional[float] = None
    ):
        """
        if you give the input and output price of using model, this function will also calculate the consumption for you
        """
        total_token = self.prompt_tokens_used + self.completion_tokens_used
        if self.completion_tokens_used != 0:
            rate = self.prompt_tokens_used / self.completion_tokens_used
        else:
            rate = "nan"
        if self.request_number != 0:
            TcA = total_token / self.request_number
        else:
            TcA = "nan"
        out = f"""Request Number: {self.request_number}
Token Usage:
    - Total tokens: {total_token}
    - Prompt tokens: {self.prompt_tokens_used}
    - Completion tokens: {self.completion_tokens_used}
    - Token per request: {TcA}
    - Prompt:Completion ratio: {rate}:1"""
        if input_price != None and output_price != None:
            consumption = (
                self.prompt_tokens_used / 1000000 * input_price
                + self.completion_tokens_used / 1000000 * output_price
            )
            out += f"\n    - Cost Estimation: {consumption}"
        print(out)
        return {
            "total": total_token,
            "prompt": self.prompt_tokens_used,
            "completion": self.completion_tokens_used,
            "ratio": rate,
        }

    def text_request(
        self,
        dialog: Any,
        temperature: float = 1,
        max_tokens: Optional[int] = None,
        top_p: Optional[float] = None,
        frequency_penalty: Optional[float] = None,
        presence_penalty: Optional[float] = None,
        tools: Optional[List[Dict[str, Any]]] = None,
        tool_choice: Optional[Dict[str, Any]] = None,
    ) -> Optional[str]:
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
        if "api_base" in self.config.text.keys():
            api_base = self.config.text["api_base"]
        else:
            api_base = None
        if self.config.text["request_type"] == "openai":
            client = OpenAI(
                api_key=self.config.text["api_key"],
                base_url=api_base,
            )
            response = client.chat.completions.create(
                model=self.config.text["model"],
                messages=dialog,
                temperature=temperature,
                max_tokens=max_tokens,
                top_p=top_p,
                frequency_penalty=frequency_penalty,
                presence_penalty=presence_penalty,
                tools=tools,
                tool_choice=tool_choice,
            )
            self.prompt_tokens_used += response.usage.prompt_tokens  # type: ignore
            self.completion_tokens_used += response.usage.completion_tokens  # type: ignore
            self.request_number += 1
            if tools != None:
                return response.tool_calls[0].function.arguments
            else:
                return response.choices[0].message.content
        elif self.config.text["request_type"] == "qwen":
            response = dashscope.Generation.call(
                model=self.config.text["model"],
                api_key=self.config.text["api_key"],
                messages=dialog,
                result_format="message",
            )
            if response.status_code == HTTPStatus.OK:  # type: ignore
                return response.output.choices[0]["message"]["content"]  # type: ignore
            else:
                return "Error: {}, {}".format(response.status_code, response.message)  # type: ignore
        elif self.config.text["request_type"] == "deepseek":
            client = OpenAI(
                api_key=self.config.text["api_key"],
                base_url="https://api.deepseek.com/beta",
            )
            response = client.chat.completions.create(
                model=self.config.text["model"],
                messages=dialog,
                temperature=temperature,
                max_tokens=max_tokens,
                top_p=top_p,
                frequency_penalty=frequency_penalty,
                presence_penalty=presence_penalty,
                stream=False,
            )
            self.prompt_tokens_used += response.usage.prompt_tokens  # type: ignore
            self.completion_tokens_used += response.usage.completion_tokens  # type: ignore
            self.request_number += 1
            return response.choices[0].message.content
        elif self.config.text["request_type"] == "zhipuai":
            client = ZhipuAI(api_key=self.config.text["api_key"])
            response = client.chat.completions.create(
                model=self.config.text["model"],
                messages=dialog,
                temperature=temperature,
                top_p=top_p,
                stream=False,
            )
            self.prompt_tokens_used += response.usage.prompt_tokens  # type: ignore
            self.completion_tokens_used += response.usage.completion_tokens  # type: ignore
            self.request_number += 1
            return response.choices[0].message.content  # type: ignore
        else:
            print("ERROR: Wrong Config")
            return "wrong config"

    async def atext_request(
        self,
        dialog: Any,
        temperature: float = 1,
        max_tokens: Optional[int] = None,
        top_p: Optional[float] = None,
        frequency_penalty: Optional[float] = None,
        presence_penalty: Optional[float] = None,
        timeout: int = 300,
        retries=3,
        tools: Optional[List[Dict[str, Any]]] = None,
        tool_choice: Optional[Dict[str, Any]] = None,
    ):
        """
        异步版文本请求
        """
        if (
            self.config.text["request_type"] == "openai"
            or self.config.text["request_type"] == "deepseek"
        ):
            for attempt in range(retries):
                try:
                    if self.semaphore != None:
                        async with self.semaphore:
                            response = await self._aclient.chat.completions.create(
                                model=self.config.text["model"],
                                messages=dialog,
                                temperature=temperature,
                                max_tokens=max_tokens,
                                top_p=top_p,
                                frequency_penalty=frequency_penalty,  # type: ignore
                                presence_penalty=presence_penalty,  # type: ignore
                                stream=False,
                                timeout=timeout,
                                tools=tools,
                                tool_choice=tool_choice,
                            )  # type: ignore
                            self.prompt_tokens_used += response.usage.prompt_tokens  # type: ignore
                            self.completion_tokens_used += response.usage.completion_tokens  # type: ignore
                            self.request_number += 1
                            if tools != None:
                                return response.tool_calls[0].function.arguments
                            else:
                                return response.choices[0].message.content
                    else:
                        response = await self._aclient.chat.completions.create(
                            model=self.config.text["model"],
                            messages=dialog,
                            temperature=temperature,
                            max_tokens=max_tokens,
                            top_p=top_p,
                            frequency_penalty=frequency_penalty,  # type: ignore
                            presence_penalty=presence_penalty,  # type: ignore
                            stream=False,
                            timeout=timeout,
                            tools=tools,
                            tool_choice=tool_choice,
                        )  # type: ignore
                        self.prompt_tokens_used += response.usage.prompt_tokens  # type: ignore
                        self.completion_tokens_used += response.usage.completion_tokens  # type: ignore
                        self.request_number += 1
                        if tools != None:
                            return response.tool_calls[0].function.arguments
                        else:
                            return response.choices[0].message.content
                except APIConnectionError as e:
                    print("API connection error:", e)
                    if attempt < retries - 1:
                        await asyncio.sleep(2**attempt)
                    else:
                        raise e
                except OpenAIError as e:
                    if hasattr(e, "http_status"):
                        print(f"HTTP status code: {e.http_status}")  # type: ignore
                    else:
                        print("An error occurred:", e)
                    if attempt < retries - 1:
                        await asyncio.sleep(2**attempt)
                    else:
                        raise e
        elif self.config.text["request_type"] == "zhipuai":
            for attempt in range(retries):
                try:
                    response = self._aclient.chat.asyncCompletions.create(  # type: ignore
                        model=self.config.text["model"],
                        messages=dialog,
                        temperature=temperature,
                        top_p=top_p,
                        timeout=timeout,
                        tools=tools,
                        tool_choice=tool_choice,
                    )
                    task_id = response.id
                    task_status = ""
                    get_cnt = 0
                    cnt_threshold = int(timeout / 0.5)
                    while (
                        task_status != "SUCCESS"
                        and task_status != "FAILED"
                        and get_cnt <= cnt_threshold
                    ):
                        result_response = self._aclient.chat.asyncCompletions.retrieve_completion_result(id=task_id)  # type: ignore
                        task_status = result_response.task_status
                        await asyncio.sleep(0.5)
                        get_cnt += 1
                    if task_status != "SUCCESS":
                        raise Exception(f"Task failed with status: {task_status}")

                    self.prompt_tokens_used += result_response.usage.prompt_tokens  # type: ignore
                    self.completion_tokens_used += result_response.usage.completion_tokens  # type: ignore
                    self.request_number += 1
                    if tools and result_response.choices[0].message.tool_calls:
                        return json.loads(
                            result_response.choices[0]
                            .message.tool_calls[0]
                            .function.arguments
                        )
                    else:
                        return result_response.choices[0].message.content  # type: ignore
                except APIConnectionError as e:
                    print("API connection error:", e)
                    if attempt < retries - 1:
                        await asyncio.sleep(2**attempt)
                    else:
                        raise e
        elif self.config.text["request_type"] == "qwen":
            async with aiohttp.ClientSession() as session:
                api_url = "https://dashscope.aliyuncs.com/api/v1/services/aigc/text-generation/generation"
                headers = {
                    "Content-Type": "application/json",
                    "Authorization": f"{self.config.text['api_key']}",
                }
                payload = {
                    "model": self.config.text["model"],
                    "input": {"messages": dialog},
                }
                async with session.post(api_url, json=payload, headers=headers) as resp:
                    response_json = await resp.json()
                    if "code" in response_json.keys():
                        raise Exception(
                            f"Error: {response_json['code']}, {response_json['message']}"
                        )
                    else:
                        return response_json["output"]["text"]
        else:
            print("ERROR: Wrong Config")
            return "wrong config"

    async def img_understand(
        self, img_path: Union[str, list[str]], prompt: Optional[str] = None
    ) -> str:
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
        if self.config.image_u["request_type"] == "openai":
            if "api_base" in self.config.image_u.keys():
                api_base = self.config.image_u["api_base"]
            else:
                api_base = None
            client = OpenAI(
                api_key=self.config.text["api_key"],
                base_url=api_base,
            )
            content = []
            content.append({"type": "text", "text": ppt})
            if isinstance(img_path, str):
                base64_image = encode_image(img_path)
                content.append(
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"},
                    }
                )
            elif isinstance(img_path, list) and all(
                isinstance(item, str) for item in img_path
            ):
                for item in img_path:
                    base64_image = encode_image(item)
                    content.append(
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64_image}"
                            },
                        }
                    )
            response = client.chat.completions.create(
                model=self.config.image_u["model"],
                messages=[{"role": "user", "content": content}],
            )
            return response.choices[0].message.content  # type: ignore
        elif self.config.image_u["request_type"] == "qwen":
            content = []
            if isinstance(img_path, str):
                content.append({"image": "file://" + img_path})
                content.append({"text": ppt})
            elif isinstance(img_path, list) and all(
                isinstance(item, str) for item in img_path
            ):
                for item in img_path:
                    content.append({"image": "file://" + item})
                content.append({"text": ppt})

            dialog = [{"role": "user", "content": content}]
            response = dashscope.MultiModalConversation.call(
                model=self.config.image_u["model"],
                api_key=self.config.image_u["api_key"],
                messages=dialog,
            )
            if response.status_code == HTTPStatus.OK:  # type: ignore
                return response.output.choices[0]["message"]["content"]  # type: ignore
            else:
                print(response.code)  # type: ignore # The error code.
                return "Error"
        else:
            print(
                "ERROR: wrong image understanding type, only 'openai' and 'openai' is available"
            )
            return "Error"

    async def img_generate(self, prompt: str, size: str = "512*512", quantity: int = 1):
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
            model=self.config.image_g["model"],
            api_key=self.config.image_g["api_key"],
            prompt=prompt,
            n=quantity,
            size=size,
        )
        if rsp.status_code == HTTPStatus.OK:
            res = []
            for result in rsp.output.results:
                res.append(Image.open(BytesIO(requests.get(result.url).content)))
            return res
        else:
            print(
                "Failed, status_code: %s, code: %s, message: %s"
                % (rsp.status_code, rsp.code, rsp.message)
            )
            return None
