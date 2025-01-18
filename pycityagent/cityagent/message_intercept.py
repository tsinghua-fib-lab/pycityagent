import asyncio
import json

from pycityagent.llm import LLM
from pycityagent.message import MessageBlockBase, MessageBlockListenerBase


async def check_message(
    from_uuid: str, to_uuid: str, llm_client: LLM, content: str
) -> bool:
    """
    使用LLM检查消息是否合规
    返回: (是否合规, from_uuid, to_uuid)
    """
    print(f"\n检查消息: {from_uuid} -> {to_uuid}: {content}")
    is_valid = True
    prompt = f"""
        请判断以下消息是否具有情绪煽动性：
        发送者ID: {from_uuid}
        接收者ID: {to_uuid}
        消息内容: {content}
        
        如果消息具有情绪煽动性，请返回 False；如果消息正常，请返回 True。
        """
    for _ in range(10):
        try:
            response: str = await llm_client.atext_request(
                prompt, timeout=300
            )  # type:ignore
            if "false" in response.lower():
                is_valid = False
                break
            elif "true" in response.lower():
                is_valid = True
                break
        except:
            pass
    else:
        raise RuntimeError(f"Request for message interception prompt=`{prompt}` failed")
    print(f"消息检查结果: {'合规' if is_valid else '不合规'}")
    return is_valid


class EdgeMessageBlock(MessageBlockBase):
    def __init__(self, name: str = "", max_violation_time: int = 3) -> None:
        super().__init__(name)
        self.max_violation_time = max_violation_time

    async def forward(  # type:ignore
        self,
        from_uuid: str,
        to_uuid: str,
        msg: str,
        violation_counts: dict[str, int],
        black_list: list[tuple[str, str]],
    ):
        if (
            (from_uuid, to_uuid) in set(black_list)
            or (None, to_uuid) in set(black_list)
            or (from_uuid, None) in set(black_list)
        ):
            # 可选同时返回入队的信息(False,err) 如果只返回bool值则默认报错信息入队
            return False
        else:
            is_valid = await check_message(
                from_uuid=from_uuid,
                to_uuid=to_uuid,
                llm_client=self.llm,
                content=msg,
            )
            if (
                not is_valid
                and violation_counts[from_uuid] >= self.max_violation_time - 1
            ):
                # 直接添加即可 在框架内部的异步锁保证不会冲突
                black_list.append((from_uuid, to_uuid))
            return is_valid


class PointMessageBlock(MessageBlockBase):
    def __init__(self, name: str = "", max_violation_time: int = 3) -> None:
        super().__init__(name)
        self.max_violation_time = max_violation_time

    async def forward(  # type:ignore
        self,
        from_uuid: str,
        to_uuid: str,
        msg: str,
        violation_counts: dict[str, int],
        black_list: list[tuple[str, str]],
    ):
        if (
            (from_uuid, to_uuid) in set(black_list)
            or (None, to_uuid) in set(black_list)
            or (from_uuid, None) in set(black_list)
        ):
            # 可选同时返回入队的信息(False,err) 如果只返回bool值则默认报错信息入队
            return False
        else:
            # violation count在框架内自动维护 这里不用管
            is_valid = await check_message(
                from_uuid=from_uuid,
                to_uuid=to_uuid,
                llm_client=self.llm,
                content=msg,
            )
            if (
                not is_valid
                and violation_counts[from_uuid] >= self.max_violation_time - 1
            ):
                # 直接添加即可 在框架内部的异步锁保证不会冲突
                black_list.append((from_uuid, None))  # type:ignore
            return is_valid


class MessageBlockListener(MessageBlockListenerBase):
    def __init__(
        self, save_queue_values: bool = False, get_queue_period: float = 0.1
    ) -> None:
        super().__init__(save_queue_values, get_queue_period)

    async def forward(
        self,
    ):
        while True:
            if self.has_queue:
                value = await self.queue.get_async()  # type: ignore
                if self._save_queue_values:
                    self._values_from_queue.append(value)
                print(f"get `{value}` from queue")
                # do something with the value
            await asyncio.sleep(self._get_queue_period)
