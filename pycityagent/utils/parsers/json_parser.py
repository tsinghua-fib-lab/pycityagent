import json
import logging
from typing import Any

from .parser_base import ParserBase


class JsonObjectParser(ParserBase):
    """A parser that extracts and parses JSON objects from a response string enclosed within specific tags.

    Attributes:
        tag_start (str): The start tag used to identify the beginning of the JSON object.
        tag_end (str): The end tag used to identify the end of the JSON object.
    """

    tag_start = "```json"
    tag_end = "```"

    def __init__(self) -> None:
        """Initialize the JsonObjectParser with default tags."""
        super().__init__()

    def parse(self, response: str) -> Any:
        """Parse the response string to extract and return a JSON object.

        Parameters:
            response (str): The response string containing the JSON object.

        Returns:
            Any: The parsed JSON object.
        """
        extract_text = self._extract_text_within_tags(
            response=response,
            tag_start=self.tag_start,
            tag_end=self.tag_end,
        )
        try:
            eval_parsed_json = eval(extract_text)
            return eval_parsed_json
        except Exception as e:
            # logging.warning(f"Error when handling text {extract_text} with `eval`")
            pass
        try:
            parsed_json = json.loads(extract_text)
            return parsed_json
        except json.decoder.JSONDecodeError as e:
            raw_response = f"{self.tag_start}{extract_text}{self.tag_end}"
            raise ValueError(
                f"The content between {self.tag_start} and {self.tag_end} "
                f"MUST be a JSON object."
                f'When parsing "{raw_response}", an error occurred: {e}',
            ) from None


class JsonDictParser(JsonObjectParser):
    """A parser that extends JsonObjectParser to ensure the parsed JSON is returned as a dictionary.

    Attributes:
        tag_start (str): The start tag used to identify the beginning of the JSON object.
        tag_end (str): The end tag used to identify the end of the JSON object.
    """

    tag_start = "```json"
    tag_end = "```"

    def __init__(self) -> None:
        """Initialize the JsonDictParser with default tags."""
        super().__init__()

    def parse(self, response: str) -> dict:
        """Parse the response string to extract and return a JSON object as a dictionary.

        Parameters:
            response (str): The response string containing the JSON object.

        Returns:
            dict: The parsed JSON object as a dictionary.
        """
        parsed_json = super().parse(response)
        if not isinstance(parsed_json, dict):
            # If not a dictionary, raise an error
            raise ValueError(
                "A JSON dictionary object is wanted, "
                f"but got {type(parsed_json)} instead."
            )
        return dict(parsed_json)
