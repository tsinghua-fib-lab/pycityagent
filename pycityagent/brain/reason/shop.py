from ..scheduler import *

async def startShop(wk):
    """
    是否开始购物
    Whether start shopping

    Args:
    - wk (WorkingMemory)

    Returns:
    - (bool): if True, start, else not
    """
    if not wk.enable_economy:
        return False
    now = wk.scheduler.now
    if now != None and now.type.value == ScheduleType.SHOP.value:
        if now.arrived and not now.finished:
            return True
    return False

async def endShop(wk):
    """
    判断是否结束购物
    Whether end shopping

    Args:
    - wk (WorkingMemory)

    Returns:
    - (bool): if True, stop, else not
    """
    now = wk.scheduler.now
    if now != None and now.type.value == ScheduleType.SHOP.value:
        if now.finished:
            return True
    return False