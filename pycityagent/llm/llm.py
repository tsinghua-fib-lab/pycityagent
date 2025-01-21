"""UrbanLLM: 智能能力类及其定义"""

import json
import logging

from openai import APIConnectionError, AsyncOpenAI, OpenAI, OpenAIError
from zhipuai import ZhipuAI

logging.getLogger("zhipuai").setLevel(logging.WARNING)

import asyncio
import os
from http import HTTPStatus
from io import BytesIO
from typing import Any, Optional, Union

import dashscope
import requests
from dashscope import ImageSynthesis
from PIL import Image

from .llmconfig import *
from .utils import *

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
        self._current_client_index = 0

        api_keys = self.config.text["api_key"]
        if not isinstance(api_keys, list):
            api_keys = [api_keys]

        self._aclients = []
        self._client_usage = []

        for api_key in api_keys:
            if self.config.text["request_type"] == "openai":
                client = AsyncOpenAI(api_key=api_key, timeout=300)
            elif self.config.text["request_type"] == "deepseek":
                client = AsyncOpenAI(
                    api_key=api_key,
                    base_url="https://api.deepseek.com/v1",
                    timeout=300,
                )
            elif self.config.text["request_type"] == "qwen":
                client = AsyncOpenAI(
                    api_key=api_key,
                    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
                    timeout=300,
                )
            elif self.config.text["request_type"] == "zhipuai":
                client = ZhipuAI(api_key=api_key, timeout=300)
            else:
                raise ValueError(
                    f"Unsupported `request_type` {self.config.text['request_type']}!"
                )
            self._aclients.append(client)
            self._client_usage.append({
                "prompt_tokens": 0,
                "completion_tokens": 0,
                "request_number": 0
            })

    def set_semaphore(self, number_of_coroutine: int):
        self.semaphore = asyncio.Semaphore(number_of_coroutine)

    def clear_semaphore(self):
        self.semaphore = None

    def clear_used(self):
        """
        clear the storage of used tokens to start a new log message
        Only support OpenAI category API right now, including OpenAI, Deepseek
        """
        for usage in self._client_usage:
            usage["prompt_tokens"] = 0
            usage["completion_tokens"] = 0 
            usage["request_number"] = 0

    def get_consumption(self):
        consumption = {}
        for i, usage in enumerate(self._client_usage):
            consumption[f"api-key-{i+1}"] = {
                "total_tokens": usage["prompt_tokens"] + usage["completion_tokens"],
                "request_number": usage["request_number"]
            }
        return consumption

    def show_consumption(
        self, input_price: Optional[float] = None, output_price: Optional[float] = None
    ):
        """
        Show consumption for each API key separately
        """
        total_stats = {
            "total": 0,
            "prompt": 0,
            "completion": 0,
            "requests": 0
        }
        
        for i, usage in enumerate(self._client_usage):
            prompt_tokens = usage["prompt_tokens"]
            completion_tokens = usage["completion_tokens"]
            requests = usage["request_number"]
            total_tokens = prompt_tokens + completion_tokens
            
            total_stats["total"] += total_tokens
            total_stats["prompt"] += prompt_tokens
            total_stats["completion"] += completion_tokens
            total_stats["requests"] += requests
            
            rate = prompt_tokens / completion_tokens if completion_tokens != 0 else "nan"
            tokens_per_request = total_tokens / requests if requests != 0 else "nan"
            
            print(f"\nAPI Key #{i+1}:")
            print(f"Request Number: {requests}")
            print("Token Usage:")
            print(f"    - Total tokens: {total_tokens}")
            print(f"    - Prompt tokens: {prompt_tokens}")
            print(f"    - Completion tokens: {completion_tokens}")
            print(f"    - Token per request: {tokens_per_request}")
            print(f"    - Prompt:Completion ratio: {rate}:1")
            
            if input_price is not None and output_price is not None:
                consumption = (prompt_tokens / 1000000 * input_price + 
                             completion_tokens / 1000000 * output_price)
                print(f"    - Cost Estimation: {consumption}")
        
        return total_stats

    def _get_next_client(self):
        """获取下一个要使用的客户端"""
        client = self._aclients[self._current_client_index]
        self._current_client_index = (self._current_client_index + 1) % len(
            self._aclients
        )
        return client

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
        tools: Optional[list[dict[str, Any]]] = None,
        tool_choice: Optional[dict[str, Any]] = None,
    ):
        """
        异步版文本请求
        """
        if (
            self.config.text["request_type"] == "openai"
            or self.config.text["request_type"] == "deepseek"
            or self.config.text["request_type"] == "qwen"
        ):
            for attempt in range(retries):
                try:
                    client = self._get_next_client()
                    if self.semaphore != None:
                        async with self.semaphore:
                            response = await client.chat.completions.create(
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
                            self._client_usage[self._current_client_index]["prompt_tokens"] += response.usage.prompt_tokens  # type: ignore
                            self._client_usage[self._current_client_index]["completion_tokens"] += response.usage.completion_tokens  # type: ignore
                            self._client_usage[self._current_client_index]["request_number"] += 1
                            if tools and response.choices[0].message.tool_calls:
                                return json.loads(
                                    response.choices[0]
                                    .message.tool_calls[0]
                                    .function.arguments
                                )
                            else:
                                return response.choices[0].message.content
                    else:
                        response = await client.chat.completions.create(
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
                        self._client_usage[self._current_client_index]["prompt_tokens"] += response.usage.prompt_tokens  # type: ignore
                        self._client_usage[self._current_client_index]["completion_tokens"] += response.usage.completion_tokens  # type: ignore
                        self._client_usage[self._current_client_index]["request_number"] += 1
                        if tools and response.choices[0].message.tool_calls:
                            return json.loads(
                                response.choices[0]
                                .message.tool_calls[0]
                                .function.arguments
                            )
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
                    client = self._get_next_client()
                    response = client.chat.asyncCompletions.create(  # type: ignore
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
                        result_response = client.chat.asyncCompletions.retrieve_completion_result(id=task_id)  # type: ignore
                        task_status = result_response.task_status
                        await asyncio.sleep(0.5)
                        get_cnt += 1
                    if task_status != "SUCCESS":
                        raise Exception(f"Task failed with status: {task_status}")

                    self._client_usage[self._current_client_index]["prompt_tokens"] += result_response.usage.prompt_tokens  # type: ignore
                    self._client_usage[self._current_client_index]["completion_tokens"] += result_response.usage.completion_tokens  # type: ignore
                    self._client_usage[self._current_client_index]["request_number"] += 1
                    if tools and result_response.choices[0].message.tool_calls:  # type: ignore
                        return json.loads(
                            result_response.choices[0]  # type: ignore
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
