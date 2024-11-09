from typing import Any, Callable, Dict, List, Optional, Union
from .context import Context
from .prompt import FormatPrompt
from ..llm import LLM

class Block:
    """Base class for creating a block in a workflow.

    Attributes:
        context (Context): Context object containing variable data.
        title (str): Title of the block.
        description (Optional[str]): Description of the block.
        format_prompt (Optional[FormatPrompt]): Format prompt for generating inputs.
        next_blocks (List[Block]): List of subsequent blocks to execute.
    """
    def __init__(self, context: Context, title: str, description: Optional[str] = None) -> None:
        self.context = context
        self.title = title
        self.description = description
        self.format_prompt: Optional[FormatPrompt] = None
        self.next_blocks: List[Block] = []

    async def execute(self) -> None:
        """Execute the block logic. Must be implemented by subclasses."""
        raise NotImplementedError

    def add_next_block(self, block: 'Block') -> None:
        """Add a subsequent block to be executed after this block.

        Args:
            block (Block): The block to add to the next execution sequence.
        """
        self.next_blocks.append(block)

    def __str__(self) -> str:
        """String representation of the block."""
        return f"Block Title: {self.title}, Description: {self.description}, Context: {self.context}"
    
    async def run_independently(self) -> Any:
        """Run the block logic independently without proceeding to the next block.

        Returns:
            Any: Result of the execution, if applicable.
        """
        if isinstance(self, ReasonBlock):
            if self.format_prompt and self.llm:
                self.format_prompt.format(**{key: await self.context.get(key) for key in self.format_prompt.variables})
                return await self.llm.atext_request(self.format_prompt.to_dialog())
            elif self.self_define_function:
                return self.self_define_function(self.context)
        elif isinstance(self, ActionBlock):
            print("ActionBlock")
            return None
        elif isinstance(self, RouteBlock):
            return self.selector(self.context)
            # Do not proceed to the next block

class ReasonBlock(Block):
    """Block for reasoning processing with optional LLM integration.

    Attributes:
        format_template (Optional[str]): Template for formatting prompts.
        self_define_function (Optional[Callable[[Context], Any]]): Custom function for handling logic.
        llm (Optional[LLM]): LLM instance for processing requests.
    """
    def __init__(
        self,
        context: Context,
        title: str,
        description: Optional[str] = None,
        format_template: Optional[str] = None,
        self_define_function: Optional[Callable[[Context], Any]] = None,
        llm: Optional[LLM] = None
    ) -> None:
        super().__init__(context, title, description)
        if (format_template is None) == (self_define_function is None):
            raise ValueError("Either format_template or self_define_function must be provided, but not both.")
        self.format_prompt = FormatPrompt(format_template) if format_template else None
        self.self_define_function = self_define_function
        self.llm = llm

    async def execute(self) -> None:
        """Execute the reasoning logic, updating the context as necessary."""
        if self.format_prompt and self.llm:
            self.format_prompt.format(**{key: await self.context.get(key) for key in self.format_prompt.variables})
            response = await self.llm.atext_request(self.format_prompt.to_dialog())
            # TODO: Only support one update right now
            for key in self.context.update_keys:
                self.context.update(key, response)
        elif self.self_define_function:
            response = self.self_define_function(self.context)
            for key in self.context.update_keys:
                self.context.update(key, response)
        if self.next_blocks:
            await self.next_blocks[0].execute()

    def set_next_block(self, block: 'Block') -> None:
        """Set the next block in the execution sequence.

        Args:
            block (Block): The next block to execute.
        """
        self.next_blocks = [block]

class RouteBlock(Block):
    """Block for routing to different subsequent blocks based on context.

    Attributes:
        selector (Callable[[Context], int]): Function to select which block to execute next.
    """
    def __init__(
            self, 
            context: Context, 
            selector: Callable[[Context], int], 
            title: str, 
            description: Optional[str] = None, 
            format_template: Optional[str] = None, 
            llm: Optional[LLM] = None) -> None:
        super().__init__(context, title, description)
        self.selector = selector
        self.format_prompt = FormatPrompt(format_template) if format_template else None
        self.llm = llm
    def show_selection_to_block(self) -> None:
        """Display the available selections for the next blocks."""
        for index, block in enumerate(self.next_blocks):
            print(f"Selector Index {index}: Block Title - {block.title}, Description - {block.description}")

    async def execute(self) -> None:
        """Execute the routing logic and transition to the selected next block."""
        if self.format_prompt and self.llm:
            self.format_prompt.format(**{key: await self.context.get(key) for key in self.format_prompt.variables})
            response = await self.llm.atext_request(self.format_prompt.to_dialog())
            # TODO: Only support one temp right now
            self.context.temp[self.context.temp_keys[0]] = response
        selected_index = self.selector(self.context)
        if 0 <= selected_index < len(self.next_blocks):
            await self.next_blocks[selected_index].execute()

class ActionBlock(Block):
    """Block for executing actions with a specified action function.

    Attributes:
        action_function (Callable[[Context], None]): The action to perform with the context.
    """
    def __init__(self, context: Context, action_function: Callable[[Context], None], title: str, description: Optional[str] = None) -> None:
        super().__init__(context, title, description)
        self.action_function = action_function

    async def execute(self) -> None:
        """Execute the action function and transition to the next block."""
        self.action_function(self.context)
        if self.next_blocks:
            await self.next_blocks[0].execute()

    def set_next_block(self, block: 'Block') -> None:
        """Set the next block to execute after this action.

        Args:
            block (Block): The next block to execute.
        """
        self.next_blocks = [block]