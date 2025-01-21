import asyncio
import socket
from typing import Optional

from ..environment import Simulator
from ..memory import Memory

KEY_TRIGGER_COMPONENTS = [Memory, Simulator]

__all__ = [
    "EventTrigger",
    "MemoryChangeTrigger",
    "TimeTrigger",
]


class EventTrigger:
    """Base class for event triggers that wait for specific conditions to be met.

    - **Attributes**:
        - `required_components` (List[Type]): A list of component types required by this trigger.
    """

    # 定义该trigger需要的组件类型
    required_components: list[type] = []

    def __init__(self, block=None):
        """
        - **Description**:
            - Initializes the EventTrigger with an optional block which contains dependencies.

        - **Args**:
            - `block`: An object containing necessary dependencies for the trigger. Defaults to None.
        """
        self.block = block
        if block is not None:
            self.initialize()

    def initialize(self) -> None:
        """
        - **Description**:
            - Initialize the trigger with necessary dependencies and checks for missing components.

        - **Raises**:
            - `RuntimeError`: If the block is not set or required components are missing.
        """
        if not self.block:
            raise RuntimeError("Block not set for trigger")

        # 检查所需组件是否都存在
        missing_components = []
        for component_type in self.required_components:
            component_name = component_type.__name__.lower()
            if not hasattr(self.block, component_name):
                missing_components.append(component_type.__name__)

        if missing_components:
            raise RuntimeError(
                f"Block is missing required components for {self.__class__.__name__}: "
                f"{', '.join(missing_components)}"
            )

    async def wait_for_trigger(self) -> None:
        """
        - **Description**:
            - Wait for the event trigger to be activated.

        - **Raises**:
            - `NotImplementedError`: Subclasses must implement this method.
        """
        raise NotImplementedError


class MemoryChangeTrigger(EventTrigger):
    """Event trigger that activates when a specific key in memory changes.

    - **Attributes**:
        - `required_components` (List[Type]): Specifies that the Memory component is required.
    """

    required_components = [Memory]

    def __init__(self, key: str) -> None:
        """
        - **Description**:
            - Initialize the memory change trigger.

        - **Args**:
            - `key` (str): The key in memory to monitor for changes.
        """
        self.key = key
        self.trigger_event = asyncio.Event()
        self._initialized = False
        super().__init__()

    def initialize(self) -> None:
        """
        - **Description**:
            - Initialize the trigger with memory from block and add watcher for the specified key.

        - **Raises**:
            - `RuntimeError`: If the block is not properly set.
        """
        super().initialize()  # 首先检查必需组件
        assert self.block is not None
        self.memory = self.block.memory
        asyncio.create_task(self.memory.add_watcher(self.key, self.trigger_event.set))
        self._initialized = True

    async def wait_for_trigger(self) -> None:
        """
        - **Description**:
            - Wait for the memory change trigger to be activated.

        - **Raises**:
            - `RuntimeError`: If the trigger is not properly initialized.
        """
        if not self._initialized:
            raise RuntimeError("Trigger not properly initialized")
        await self.trigger_event.wait()
        self.trigger_event.clear()


class TimeTrigger(EventTrigger):
    """Event trigger that activates periodically based on time intervals.

    - **Attributes**:
        - `required_components` (List[Type]): Specifies that the Simulator component is required.
    """

    required_components = [Simulator]

    def __init__(
        self,
        days: Optional[int] = None,
        hours: Optional[int] = None,
        minutes: Optional[int] = None,
    ) -> None:
        """
        - **Description**:
            - Initialize the time trigger with interval settings.

        - **Args**:
            - `days` (Optional[int]): Execute every N days. Defaults to None.
            - `hours` (Optional[int]): Execute every N hours. Defaults to None.
            - `minutes` (Optional[int]): Execute every N minutes. Defaults to None.

        - **Raises**:
            - `ValueError`: If all interval parameters are None or any of them are negative.
        """
        if all(param is None for param in (days, hours, minutes)):
            raise ValueError("At least one time interval must be specified")

        # 验证参数有效性
        for param_name, param_value in [
            ("days", days),
            ("hours", hours),
            ("minutes", minutes),
        ]:
            if param_value is not None and param_value < 0:
                raise ValueError(f"{param_name} cannot be negative")

        # 将所有时间间隔转换为秒
        self.interval = 0
        if days is not None:
            self.interval += days * 24 * 60 * 60
        if hours is not None:
            self.interval += hours * 60 * 60
        if minutes is not None:
            self.interval += minutes * 60

        self.trigger_event = asyncio.Event()
        self._initialized = False
        self._monitoring_task = None
        self._last_trigger_time = None
        super().__init__()

    def initialize(self) -> None:
        """
        - **Description**:
            - Initialize the trigger with necessary dependencies and start monitoring task.

        - **Raises**:
            - `RuntimeError`: If the block is not properly set.
        """
        super().initialize()  # 首先检查必需组件
        assert self.block is not None
        self.memory = self.block.memory
        self.simulator = self.block.simulator
        # 启动时间监控任务
        self._monitoring_task = asyncio.create_task(self._monitor_time())
        self._initialized = True

    async def _monitor_time(self):
        """
        - **Description**:
            - Continuously monitor the time and trigger the event when the interval has passed.
        """
        # 第一次调用时直接触发
        self.trigger_event.set()

        while True:
            try:
                current_time = await self.simulator.get_time()

                # 如果是第一次或者已经过了指定的时间间隔
                if (
                    self._last_trigger_time is None
                    or current_time - self._last_trigger_time >= self.interval
                ):
                    self._last_trigger_time = current_time
                    self.trigger_event.set()

                await asyncio.sleep(5)  # 避免过于频繁的检查
            except Exception as e:
                print(f"Error in time monitoring: {e}")
                await asyncio.sleep(10)  # 发生错误时等待较长时间

    async def wait_for_trigger(self) -> None:
        """
        - **Description**:
            - Wait for the time trigger to be activated.

        - **Raises**:
            - `RuntimeError`: If the trigger is not properly initialized.
        """
        if not self._initialized:
            raise RuntimeError("Trigger not properly initialized")
        await self.trigger_event.wait()
        self.trigger_event.clear()
