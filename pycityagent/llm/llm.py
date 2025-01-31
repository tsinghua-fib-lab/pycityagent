"""UrbanLLM: 智能能力类及其定义"""

import asyncio
import json
import logging
import time
import os
from http import HTTPStatus
from io import BytesIO
from typing import Any, Optional, Union

import dashscope
import requests
from dashscope import ImageSynthesis
from openai import APIConnectionError, AsyncOpenAI, OpenAI, OpenAIError
from PIL import Image
from zhipuai import ZhipuAI

from .llmconfig import *
from .utils import *

logging.getLogger("zhipuai").setLevel(logging.WARNING)
os.environ["GRPC_VERBOSITY"] = "ERROR"

__all__ = [
    "LLM",
]


class LLM:
    """
    Main class for the Large Language Model (LLM) object used by Agent(Soul).

    - **Description**:
        - This class manages configurations and interactions with different large language model APIs.
        - It initializes clients based on the specified request type and handles token usage and consumption reporting.
    """

    def __init__(self, config: LLMConfig) -> None:
        """
        Initializes the LLM instance.

        - **Parameters**:
            - `config`: An instance of `LLMConfig` containing configuration settings for the LLM.
        """
        self.config = config
        if config.text["request_type"] not in ["openai", "deepseek", "qwen", "zhipuai", "siliconflow"]:
            raise ValueError("Invalid request type for text request")
        self.prompt_tokens_used = 0
        self.completion_tokens_used = 0
        self.request_number = 0
        self.semaphore = asyncio.Semaphore(200)
        self._current_client_index = 0
        self._log_list = []

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
            elif self.config.text["request_type"] == "siliconflow":
                client = AsyncOpenAI(
                    api_key=api_key,
                    base_url="https://api.siliconflow.cn/v1",
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

    def get_log_list(self):
        return self._log_list
    
    def clear_log_list(self):
        self._log_list = []

    def set_semaphore(self, number_of_coroutine: int):
        """
        Sets the semaphore for controlling concurrent coroutines.

        - **Parameters**:
            - `number_of_coroutine`: The maximum number of concurrent coroutines allowed.
        """
        self.semaphore = asyncio.Semaphore(number_of_coroutine)

    def clear_semaphore(self):
        """
        Clears the semaphore setting.
        """
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
        Displays token usage and optionally calculates the estimated cost based on provided prices.

        - **Parameters**:
            - `input_price`: Price per million prompt tokens. Default is None.
            - `output_price`: Price per million completion tokens. Default is None.

        - **Returns**:
            - A dictionary summarizing the token usage and, if applicable, the estimated cost.
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
        """
        Retrieves the next client to be used for making requests.

        - **Description**:
            - This method cycles through the available clients in a round-robin fashion.

        - **Returns**:
            - The next client instance to be used for making requests.
        """
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
        retries=10,
        tools: Optional[list[dict[str, Any]]] = None,
        tool_choice: Optional[dict[str, Any]] = None,
    ):
        """
        Sends an asynchronous text request to the configured LLM API.

        - **Description**:
            - Attempts to send a text request up to `retries` times with exponential backoff on failure.
            - Handles different request types and manages token usage statistics.

        - **Parameters**:
            - `dialog`: Messages to send as part of the chat completion request.
            - `temperature`: Controls randomness in the model's output. Default is 1.
            - `max_tokens`: Maximum number of tokens to generate in the response. Default is None.
            - `top_p`: Limits the next token selection to a subset of tokens with a cumulative probability above this value. Default is None.
            - `frequency_penalty`: Penalizes new tokens based on their existing frequency in the text so far. Default is None.
            - `presence_penalty`: Penalizes new tokens based on whether they appear in the text so far. Default is None.
            - `timeout`: Request timeout in seconds. Default is 300 seconds.
            - `retries`: Number of retry attempts in case of failure. Default is 3.
            - `tools`: List of dictionaries describing the tools that can be called by the model. Default is None.
            - `tool_choice`: Dictionary specifying how the model should choose from the provided tools. Default is None.

        - **Returns**:
            - A string containing the message content or a dictionary with tool call arguments if tools are used.
            - Raises exceptions if the request fails after all retry attempts.
        """
        start_time = time.time()
        log = {"request_time": start_time}
        async with self.semaphore:
            if (
                self.config.text["request_type"] == "openai"
                or self.config.text["request_type"] == "deepseek"
                or self.config.text["request_type"] == "qwen"
                or self.config.text["request_type"] == "siliconflow"
            ):
                for attempt in range(retries):
                    try:
                        client = self._get_next_client()
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
                        end_time = time.time()
                        log["consumption"] = end_time - start_time
                        log["input_tokens"] = response.usage.prompt_tokens
                        log["output_tokens"] = response.usage.completion_tokens
                        self._log_list.append(log)
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
                            print("OpenAIError:", e)
                        if attempt < retries - 1:
                            await asyncio.sleep(2**attempt)
                        else:
                            raise e
                    except Exception as e:
                        print("LLM Error (OpenAI):", e)
                        if attempt < retries - 1:
                            print(dialog)
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
                        end_time = time.time()
                        log["used_time"] = end_time - start_time
                        log["token_consumption"] = result_response.usage.prompt_tokens + result_response.usage.completion_tokens
                        self._log_list.append(log)
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
                    except Exception as e:
                        print("LLM Error:", e)
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
        Analyzes and understands images using external APIs.

        - **Args**:
            img_path (Union[str, list[str]]): Path or list of paths to the images for analysis.
            prompt (Optional[str]): Guidance text for understanding the images.

        - **Returns**:
            str: The content derived from understanding the images.
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
        Generates images based on a given prompt.

        - **Args**:
            prompt (str): Prompt for generating images.
            size (str): Size of the generated images, default is '512*512'.
            quantity (int): Number of images to generate, default is 1.

        - **Returns**:
            list[PIL.Image.Image]: List of generated PIL Image objects.
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
