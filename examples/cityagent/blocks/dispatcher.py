from pycityagent.llm.llm import LLM
from pycityagent.workflow.block import Block
from pycityagent.workflow.prompt import FormatPrompt

DISPATCHER_PROMPT = """
Based on the step information, select the most appropriate block to handle the task.
Each block has its specific functionality as described in the function schema.
        
Step information:
{step}
"""


class BlockDispatcher:
    def __init__(self, llm: LLM):
        self.llm = llm
        self.blocks: dict[str, Block] = {}
        self.prompt = FormatPrompt(DISPATCHER_PROMPT)

    def register_blocks(self, blocks: list[Block]) -> None:
        """Register multiple blocks at once"""
        for block in blocks:
            block_name = block.__class__.__name__.lower()
            self.blocks[block_name] = block

    def _get_function_schema(self) -> dict:
        """Generate function schema for LLM function call"""
        # 创建 block 选项说明
        block_descriptions = {
            name: block.description  # type: ignore
            for name, block in self.blocks.items()
        }

        return {
            "type": "function",
            "function": {
                "name": "select_block",
                "description": "Select the most appropriate block based on the step information",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "block_name": {
                            "type": "string",
                            "enum": list(self.blocks.keys()),
                            "description": f"Available blocks and their descriptions: {block_descriptions}",
                        }
                    },
                    "required": ["block_name"],
                },
            },
        }

    async def dispatch(self, step: dict) -> Block:
        """Dispatch the step to appropriate block based on LLM function call"""
        function_schema = self._get_function_schema()
        self.prompt.format(step=step)

        # Call LLM with tools schema
        function_args = await self.llm.atext_request(
            self.prompt.to_dialog(),
            tools=[function_schema],
            tool_choice={"type": "function", "function": {"name": "select_block"}},
        )

        # Parse function call result
        try:
            selected_block = function_args.get("block_name")  # type: ignore
            print(f"selected_block: {selected_block}")

            if selected_block not in self.blocks:
                raise ValueError(
                    f"Selected block '{selected_block}' not found in registered blocks"
                )

            return self.blocks[selected_block]

        except Exception as e:
            raise ValueError(f"Failed to parse LLM response: {str(e)}")
