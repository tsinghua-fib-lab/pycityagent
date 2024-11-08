import asyncio
from typing import Any, Callable, Dict, List, Optional, Union
from enum import Enum
import networkx as nx
import matplotlib.pyplot as plt
from ..memory import Memory
from .block import *
from .trigger import EventTrigger
from ..llm import LLM
import json

class WorkflowType(Enum):
    """Enum representing the type of workflows."""
    NORMAL = "Normal"
    EVENT_DRIVEN = "EventDriven"

class Workflow:
    """A class representing a workflow that can be normal or event-driven."""

    def __init__(self, workflow_type: WorkflowType, interval: Optional[int] = None, trigger: Optional[EventTrigger] = None) -> None:
        """
        Initializes a Workflow instance.
        Args:
            workflow_type (WorkflowType): The type of workflow (normal or event-driven).
            interval (Optional[int]): The interval in seconds for normal workflows.
            trigger (Optional[EventTrigger]): The event trigger for event-driven workflows.
        """
        self.workflow_type = workflow_type
        self.interval = interval
        self.trigger = trigger
        self.start_block: Optional[Block] = None
        self.is_running = False
        self.memory: Optional[Memory] = None
        self.blocks: Dict[str, Block] = {}
        self.llm: Optional[LLM] = None

    def set_start_block(self, block: Block) -> None:
        """Sets the starting block for the workflow and registers it recursively.

        Args:
            block (Block): The block to be set as the starting block.
        """
        self.start_block = block
        self._add_block_recursive(block)

    def _add_block_recursive(self, block: Block) -> None:
        """Recursively adds a block and its next blocks to the workflow.

        Args:
            block (Block): The block to add.
        """
        if block.title not in self.blocks:
            self.blocks[block.title] = block
        for next_block in block.next_blocks:
            self._add_block_recursive(next_block)

    def bind_memory(self, memory: Memory) -> None:
        """Binds memory to the workflow, applying it to all blocks.

        Args:
            memory (Memory): The memory instance to bind.
        """
        self.memory = memory
        if self.start_block:
            self._bind_memory_to_block(self.start_block, memory)

    def _bind_memory_to_block(self, block: Block, memory: Memory) -> None:
        """Recursively binds memory to a specified block and its next blocks.

        Args:
            block (Block): The block to bind memory to.
            memory (Memory): The memory instance to bind.
        """
        block.context.memory = memory
        for next_block in block.next_blocks:
            self._bind_memory_to_block(next_block, memory)

    def bind_llm(self, llm: LLM) -> None:
        """Binds a language model (LLM) to the blocks that require it.

        Args:
            llm (LLM): The language model instance to bind.
        """
        self.llm = llm
        for block in self.blocks.values():
            if isinstance(block, ReasonBlock) and block.format_prompt and block.llm is None:
                block.llm = llm
            if isinstance(block, RouteBlock) and block.format_prompt and block.llm is None:
                block.llm = llm

    async def run(self) -> None:
        """Runs the workflow based on its type (normal or event-driven)."""
        if self.workflow_type == WorkflowType.NORMAL and self.interval:
            while self.is_running:
                if self.start_block:
                    await self.start_block.execute()
                await asyncio.sleep(self.interval)
        elif self.workflow_type == WorkflowType.EVENT_DRIVEN and self.trigger:
            while self.is_running:
                await self.trigger.wait_for_trigger()
                if self.start_block:
                    await self.start_block.execute()

    def start(self) -> None:
        """Starts the workflow execution in an asynchronous task."""
        self.is_running = True
        asyncio.create_task(self.run())

    def stop(self) -> None:
        """Stops the execution of the workflow."""
        self.is_running = False

    def visualize_workflow(self, plot: bool = False) -> None:
        """Visualizes the workflow as a directed graph.

        Args:
            plot (bool): If True, displays the graph using matplotlib; if False, prints the edges.
        """
        graph = nx.DiGraph()
        if self.start_block:
            self._add_edges(graph, self.start_block)
        if plot:
            plt.figure(figsize=(10, 8))
            pos = nx.spring_layout(graph)
            nx.draw(graph, pos, with_labels=True, node_color='lightblue', font_weight='bold', node_size=2000, arrows=True)
            plt.title("Workflow Execution Graph")
            plt.show()
        else:
            for line in nx.generate_edgelist(graph, data=False):
                print(line)

    def _add_edges(self, graph: nx.DiGraph, block: Block) -> None:
        """Adds edges to the graph from the specified block to its next blocks.

        Args:
            graph (nx.DiGraph): The directed graph to add edges to.
            block (Block): The block from which to add edges.
        """
        for next_block in block.next_blocks:
            graph.add_edge(f"{block.title}", f"{next_block.title}")
            self._add_edges(graph, next_block)

    def get_block(self, title: str) -> Optional[Block]:
        """Retrieves a block by its title.

        Args:
            title (str): The title of the block.

        Returns:
            Optional[Block]: The block associated with the title, or None if not found.
        """
        return self.blocks.get(title)

    @classmethod
    def from_config(cls, config_path: str) -> 'Workflow':
        """Creates a Workflow instance from a JSON configuration file.

        Args:
            config_path (str): The path to the configuration JSON file.

        Returns:
            Workflow: The initialized workflow instance.

        Example JSON configuration file (config.json):
        {
            "workflow_type": "NORMAL",
            "interval": 10,
            "blocks": [
                {
                    "type": "ReasonBlock",
                    "title": "Start Reasoning",
                    "description": "This block starts the reasoning process.",
                    "format_template": "Hello, {name}! How can I assist you today?"
                },
                {
                    "type": "ActionBlock",
                    "title": "Print Response",
                    "description": "This block prints the response.",
                    "action_function": "print_response"
                }
            ]
        }
        """
        with open(config_path, 'r') as file:
            config_data = json.load(file)
        workflow_type = WorkflowType[config_data['workflow_type']]
        interval = config_data.get('interval')
        trigger = None  # Placeholder for initializing triggers if required
        workflow = cls(workflow_type, interval, trigger)
        # Initialize blocks based on config_data
        # Example usage of config
        return workflow

class NormalWorkflow(Workflow):
    """A class representing a normal workflow with a specified interval."""

    def __init__(self, interval: int) -> None:
        """
        Initializes a NormalWorkflow instance.

        Args:
            interval (int): The interval in seconds for executing the workflow.
        """
        super().__init__(workflow_type=WorkflowType.NORMAL, interval=interval)

class EventDrivenWorkflow(Workflow):
    """A class representing an event-driven workflow with a specified trigger."""

    def __init__(self, trigger: EventTrigger) -> None:
        """
        Initializes an EventDrivenWorkflow instance.

        Args:
            trigger (EventTrigger): The event trigger for this workflow.
        """
        super().__init__(workflow_type=WorkflowType.EVENT_DRIVEN, trigger=trigger)