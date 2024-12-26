from typing import Optional, Union
import re


class FormatPrompt:
    """
    A class to handle the formatting of prompts based on a template,
    with support for system prompts and variable extraction.

    Attributes:
        template (str): The template string containing placeholders.
        system_prompt (Optional[str]): An optional system prompt to add to the dialog.
        variables (list[str]): A list of variable names extracted from the template.
        formatted_string (str): The formatted string derived from the template and provided variables.
    """

    def __init__(self, template: str, system_prompt: Optional[str] = None) -> None:
        """
        Initializes the FormatPrompt with a template and an optional system prompt.

        Args:
            template (str): The string template with variable placeholders.
            system_prompt (Optional[str]): An optional system prompt.
        """
        self.template = template
        self.system_prompt = system_prompt  # Store the system prompt
        self.variables = self._extract_variables()
        self.formatted_string = ""  # To store the formatted string

    def _extract_variables(self) -> list[str]:
        """
        Extracts variable names from the template string.

        Returns:
            list[str]: A list of variable names found within the template.
        """
        return re.findall(r"\{(\w+)\}", self.template)

    def format(self, **kwargs) -> str:
        """
        Formats the template string using the provided keyword arguments.

        Args:
            **kwargs: Variable names and their corresponding values to format the template.

        Returns:
            str: The formatted string.
        """
        self.formatted_string = self.template.format(
            **kwargs
        )  # Store the formatted string
        return self.formatted_string

    def to_dialog(self) -> list[dict[str, str]]:
        """
        Converts the formatted prompt and optional system prompt into a dialog format.

        Returns:
            list[dict[str, str]]: A list representing the dialog with roles and content.
        """
        dialog = []
        if self.system_prompt:
            dialog.append(
                {"role": "system", "content": self.system_prompt}
            )  # Add system prompt if it exists
        dialog.append(
            {"role": "user", "content": self.formatted_string}
        )  # Add user content
        return dialog

    def log(self) -> None:
        """
        Logs the details of the FormatPrompt, including the template,
        system prompt, extracted variables, and formatted string.
        """
        print(f"FormatPrompt: {self.template}")
        print(f"System Prompt: {self.system_prompt}")  # Log the system prompt
        print(f"Variables: {self.variables}")
        print(f"Formatted String: {self.formatted_string}")  # Log the formatted string
