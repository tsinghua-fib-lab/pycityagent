"""UrbanLLM: 智能能力类及其定义"""

import asyncio
import json
import logging
import os
import time
from typing import Any, Optional, Union

from openai import APIConnectionError, AsyncOpenAI, OpenAI, OpenAIError
from zhipuai import ZhipuAI

from ..configs import LLMRequestConfig
from ..utils import LLMRequestType
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

    def __init__(self, config: LLMRequestConfig) -> None:
        """
        Initializes the LLM instance.

        - **Parameters**:
            - `config`: An instance of `LLMRequestConfig` containing configuration settings for the LLM.
        """
        self.config = config
        if config.request_type not in {t.value for t in LLMRequestType}:
            raise ValueError("Invalid request type for text request")
        self.prompt_tokens_used = 0
        self.completion_tokens_used = 0
        self.request_number = 0
        self.semaphore = asyncio.Semaphore(200)
        self._current_client_index = 0
        self._log_list = []

        api_keys = self.config.api_key
        if not isinstance(api_keys, list):
            api_keys = [api_keys]

        self._aclients = []
        self._client_usage = []

        for api_key in api_keys:
            if self.config.request_type == LLMRequestType.OpenAI:
                client = AsyncOpenAI(api_key=api_key, timeout=300)
            elif self.config.request_type == LLMRequestType.DeepSeek:
                client = AsyncOpenAI(
                    api_key=api_key,
                    base_url="https://api.deepseek.com/v1",
                    timeout=300,
                )
            elif self.config.request_type == LLMRequestType.Qwen:
                client = AsyncOpenAI(
                    api_key=api_key,
                    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
                    timeout=300,
                )
            elif self.config.request_type == LLMRequestType.SiliconFlow:
                client = AsyncOpenAI(
                    api_key=api_key,
                    base_url="https://api.siliconflow.cn/v1",
                    timeout=300,
                )
            elif self.config.request_type == LLMRequestType.ZhipuAI:
                client = ZhipuAI(api_key=api_key, timeout=300)
            else:
                raise ValueError(
                    f"Unsupported `request_type` {self.config.request_type}!"
                )
            self._aclients.append(client)
            self._client_usage.append(
                {"prompt_tokens": 0, "completion_tokens": 0, "request_number": 0}
            )

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
                "request_number": usage["request_number"],
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
        total_stats = {"total": 0, "prompt": 0, "completion": 0, "requests": 0}

        for i, usage in enumerate(self._client_usage):
            prompt_tokens = usage["prompt_tokens"]
            completion_tokens = usage["completion_tokens"]
            requests = usage["request_number"]
            total_tokens = prompt_tokens + completion_tokens

            total_stats["total"] += total_tokens
            total_stats["prompt"] += prompt_tokens
            total_stats["completion"] += completion_tokens
            total_stats["requests"] += requests

            rate = (
                prompt_tokens / completion_tokens if completion_tokens != 0 else "nan"
            )
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
                consumption = (
                    prompt_tokens / 1000000 * input_price
                    + completion_tokens / 1000000 * output_price
                )
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
        response_format: Optional[dict[str, Any]] = None,
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
            - `response_format`: JSON schema for the response. Default is None.
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
        assert (
            self.semaphore is not None
        ), "Please set semaphore with `set_semaphore` first!"
        async with self.semaphore:
            if (
                self.config.request_type == "openai"
                or self.config.request_type == "deepseek"
                or self.config.request_type == "qwen"
                or self.config.request_type == "siliconflow"
            ):
                for attempt in range(retries):
                    try:
                        client = self._get_next_client()
                        response = await client.chat.completions.create(
                            model=self.config.model,
                            messages=dialog,
                            response_format=response_format,
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
                        self._client_usage[self._current_client_index][
                            "request_number"
                        ] += 1
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
                            await asyncio.sleep(2**attempt)
                        else:
                            raise e
            elif self.config.request_type == "zhipuai":
                for attempt in range(retries):
                    try:
                        client = self._get_next_client()
                        response = client.chat.asyncCompletions.create(  # type: ignore
                            model=self.config.model,
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
                        self._client_usage[self._current_client_index][
                            "request_number"
                        ] += 1
                        end_time = time.time()
                        log["used_time"] = end_time - start_time
                        log["token_consumption"] = result_response.usage.prompt_tokens + result_response.usage.completion_tokens  # type: ignore
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
                raise ValueError("ERROR: Wrong Config")
