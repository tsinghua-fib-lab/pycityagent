import logging

from pycityagent.memory import Memory

logging.basicConfig(level=logging.INFO)


def get_test_mem() -> Memory:
    # See pycityagent.memory.const for defined memory attributes
    # self define attributes
    EXTRA_ATTRIBUTES = {
        "personal_name": str,  # type
        "debug": (bool, True),  # (type, default value)
        "extra": (dict, {"_id": 0}),  # (type, default value)
        # "id":(int,1), # key `id` overlaps with defined memory attributes, will not be added to self-define memory
    }
    # initialization and set values
    mem = Memory(config=EXTRA_ATTRIBUTES)
    mem.update_batch(
        {
            "id": 1,
            "schedules": [1, 2],
        }
    )
    return mem


def mem_test_1():
    _s = """`update` with `mode` == "replace" """
    logging.info(_s)
    test_keys = ["id", "personal_name"]
    test_values = [42, "test"]
    mem = get_test_mem()
    for _key in test_keys:
        print(f"original `{_key}`:", mem.get(_key))
    # Three ways to update the memory
    # 1.update one by one
    for _key, _value in zip(test_keys, test_values):
        mem.update(key=_key, value=_value, mode="replace")
    # 2.update in batch (sequence)
    # mem.update_batch([z for z in zip(test_keys,test_values)],mode="replace")
    # 3.update in batch (dict)
    # mem.update_batch({k:v for k,v in zip(test_keys,test_values)},mode="replace")
    for _key in test_keys:
        print(f"updated `{_key}`:", mem.get(_key))
    print()


def mem_test_2():
    _s = """`update` with `mode` == "merge" """
    logging.info(_s)
    test_keys = ["id", "schedules"]
    test_values = [42, [4, 5, 6]]
    mem = get_test_mem()
    for _key in test_keys:
        print(f"original `{_key}`:", mem.get(_key))
    # Three ways to update the memory
    # 1.update one by one
    for _key, _value in zip(test_keys, test_values):
        mem.update(key=_key, value=_value, mode="merge")
    # 2.update in batch (sequence)
    # mem.update_batch([z for z in zip(test_keys,test_values)],mode="merge")
    # 3.update in batch (dict)
    # mem.update_batch({k:v for k,v in zip(test_keys,test_values)},mode="merge")
    for _key in test_keys:
        print(f"updated `{_key}`:", mem.get(_key))
    print()


def mem_test_3():
    _s = """`get` with `mode` == "read only" """
    logging.info(_s)
    mem = get_test_mem()
    sch = mem.get(key="schedules", mode="read only")
    print("original:", sch)
    sch.append("test")
    print(f"fetched: {sch}, in memory: {mem.get(key = 'schedules')}")
    print()


def mem_test_4():
    _s = """`get` with `mode` == "read and write" """
    logging.info(_s)
    mem = get_test_mem()
    sch = mem.get(key="schedules", mode="read and write")
    print("original:", sch)
    sch.append("test")
    print(f"fetched: {sch}, in memory: {mem.get(key = 'schedules')}")
    print()


if __name__ == "__main__":
    # `update` with `mode` == "replace"
    mem_test_1()
    # `update` with `mode` == "merge"
    mem_test_2()
    # `get` with `mode` == "read only"
    mem_test_3()
    # `get` with `mode` == "read and write"
    mem_test_4()
