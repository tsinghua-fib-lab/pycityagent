import asyncio
import logging

from pycityagent.memory import Memory

logging.basicConfig(level=logging.INFO)


def init_test_mem() -> Memory:
    # self define attributes
    DEFINE_ATTRIBUTES = {
        "_field_0": str,  # type
        "_field_1": (dict, {"_id": 0}),  # (type, default value)
        "_field_2": list,  # type
        # "id":(int,1), # key `id` overlaps with defined memory attributes, will not be added to self-define memory
    }
    # initialization and set values
    # See pycityagent.memory.const for defined `base` and `motion`memory attributes
    mem = Memory(
        config=DEFINE_ATTRIBUTES,
        base={
            "id": 2024,
        },
        motion={
            "status": 1,
            "v": 10.0,
        },
        profile={
            "gender": "male",
            "education": "Doctor",
            "consumption": "sightly low",
            "occupation": "Student",
        },
        activate_timestamp=True,
    )
    return mem


async def mem_test_write():
    logging.info("Memory Writing Test\n")
    _s = """1.`update` with `mode` == "replace" """
    logging.info(_s)
    test_keys = ["_field_0", "_field_1"]
    test_values = ["updated", {"updated": 0}]
    mem = init_test_mem()
    for _key in test_keys:
        print(f"original `{_key}`:", await mem.get(_key))
    # Three ways to update the memory
    # 1.update one by one
    for _key, _value in zip(test_keys, test_values):
        await mem.update(key=_key, value=_value, mode="replace", store_snapshot=True)
    # 2.update in batch (sequence)
    # await  mem.update_batch([z for z in zip(test_keys,test_values)],mode="replace")
    # 3.update in batch (dict)
    # await mem.update_batch({k:v for k,v in zip(test_keys,test_values)},mode="replace")
    for _key in test_keys:
        print(f"updated `{_key}`:", await mem.get(_key))
    print()
    _s = """2.`update` with `mode` == "merge" """
    logging.info(_s)
    mem = init_test_mem()
    for _key in test_keys:
        print(f"original `{_key}`:", await mem.get(_key))
    for _key, _value in zip(test_keys, test_values):
        await mem.update(key=_key, value=_value, mode="merge")
    for _key in test_keys:
        print(f"updated `{_key}`:", await mem.get(_key))
    print()
    _s = """3.`update` protected fields (State Memory)"""
    logging.info(_s)
    mem = init_test_mem()
    _key = "id"
    await mem.update(key=_key, value=42)
    print(f"updated `{_key}`:", await mem.get(_key))
    await mem.update(key="id", value=42, protect_llm_read_only_fields=False)
    print(f"updated `{_key}`:", await mem.get(_key))
    _s = """4.Memory update snapshots"""
    logging.info(_s)
    mem = init_test_mem()
    # each update cause a snapshot
    for _key, _value in zip(test_keys, test_values):
        await mem.update(key=_key, value=_value, mode="replace", store_snapshot=True)
    _, _, self_define_snapshots = await mem.export()
    print("snapshots:", self_define_snapshots)  # self-define
    mem = init_test_mem()
    # one snapshot only
    await mem.update_batch(
        [(k, v) for k, v in zip(test_keys, test_values)],
        mode="replace",
        store_snapshot=True,
    )
    _, _, self_define_snapshots = await mem.export()
    print("snapshots:", self_define_snapshots)  # self-define
    print()


async def mem_test_read():
    logging.info("Memory Reading Test\n")
    _s = """1.`get` with `mode` == "read only" """
    logging.info(_s)
    mem = init_test_mem()
    temp = await mem.get(key="_field_1", mode="read only")
    print("original:", temp)
    temp.update({"new_key": 1})
    print(f"fetched: {temp}, in memory: {await mem.get(key = '_field_1')}")
    print()
    _s = """2.`get` with `mode` == "read and write" """
    logging.info(_s)
    mem = init_test_mem()
    temp = await mem.get(key="_field_1", mode="read and write")
    print("original:", temp)
    temp.update({"new_key": 1})
    print(f"fetched: {temp}, in memory: {await mem.get(key = '_field_1')}")
    print()
    _s = """3.`get top-k value` with specific metric """
    logging.info(_s)
    mem = init_test_mem()
    await mem.update("_field_2", [1, -2, 3, -4], mode="merge")
    _top_k_values = await mem.get_top_k(
        key="_field_2",
        top_k=3,
        metric=lambda x: x**2,
        mode="read only",
    )
    print(f"fetched: {_top_k_values}")
    print()


async def mem_test_load():
    logging.info("Memory Loading Test\n")
    _s = """1.`update` with `mode` == "replace" """
    logging.info(_s)
    test_keys = ["_field_0", "_field_1"]
    test_values = ["updated", {"updated": 0}]
    mem = init_test_mem()
    # one snapshot only
    await mem.update_batch(
        [(k, v) for k, v in zip(test_keys, test_values)],
        mode="replace",
        store_snapshot=True,
    )
    _, _, self_define_snapshots = snapshots = await mem.export()
    print("snapshots:    ", self_define_snapshots)  # self-define
    mem = init_test_mem()
    _, _, self_define_snapshots = await mem.export()
    print("default mem:  ", self_define_snapshots)  # self-define
    await mem.load(snapshots, reset_memory=True)
    _, _, self_define_snapshots = await mem.export()
    print("after loading:", self_define_snapshots)  # self-define


if __name__ == "__main__":
    asyncio.run(mem_test_write())
    asyncio.run(mem_test_read())
    asyncio.run(mem_test_load())
