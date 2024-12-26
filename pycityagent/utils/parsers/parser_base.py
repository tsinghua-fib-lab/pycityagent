"""
Base class of parser
"""

import re
from abc import ABC, abstractmethod
from typing import Any, Union


class ParserBase(ABC):
    def __init__(
        self,
    ) -> None:
        pass

    @abstractmethod
    def parse(self, response: str) -> Any:
        """
        Parse the string response returned by the model and convert it into a more manageable form.

        Parameters:
            response (str): The raw string returned by the model.

        Returns:
            Any: The converted data, the specific type depends on the parsing result.
        """
        pass

    def _extract_text_within_tags(
        self, response: str, tag_start: str, tag_end: str
    ) -> str:
        """
        Return the string between the first occurrence of the start tag and the end tag in the response string.

        Parameters:
            response (str): The response string.
            tag_start (str): The start tag.
            tag_end (str): The end tag.

        Returns:
            str: The string between the start and end tags.
        """

        def _extract_substring(
            text: str, tag_start: str, tag_end: str
        ) -> Union[str, None]:
            pattern = re.escape(tag_start) + r"(.*?)" + re.escape(tag_end)
            match = re.search(pattern, text, re.DOTALL)
            if match:
                return match.group(1).strip()
            else:
                return None

        sub_response = _extract_substring(response, tag_start, tag_end)
        if sub_response is not None:
            return sub_response
        else:
            raise ValueError(
                f"No text between tag {tag_start} and tag {tag_end} in response {response}!"
            )
