import logging
from typing import Any

from .parser_base import ParserBase


class CodeBlockParser(ParserBase):
    """A parser that extracts specific objects from a response string enclosed within specific tags.

    Attributes:
        tag_start (str): The start tag used to identify the beginning of the object.
        tag_end (str): The end tag used to identify the end of the object.
    """

    tag_start = "```{language_name}"
    tag_end = "```"

    def __init__(self, language_name: str) -> None:
        """Initialize the CodeBlockParser with default tags."""
        super().__init__()
        self.language_name = language_name

    def parse(self, response: str) -> str:
        """Parse the response string to extract and return a str.

        Parameters:
            response (str): The response string containing the specified language object.

        Returns:
            str: The parsed `str` object.
        """
        extract_text = self._extract_text_within_tags(
            response=response,
            tag_start=self.tag_start.format(language_name=self.language_name),
            tag_end=self.tag_end,
        )
        return extract_text
