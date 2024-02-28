from ..scheduler import *
import time

async def startTrip(wk):
    """
    判断是否开始行程
    Whether start trip

    Args:
    - wk (WorkingMemory)

    Returns:
    - (bool): if True, start target trip, else not
    """
    now = wk.scheduler.now
    if now == None:
        return False
    elif now.type.value != ScheduleType.TRIP.value:
        return False
    elif now.is_set:
        return False
    else:
        time_now = wk.sence['time']
        if now.time <= time_now:
            return True
        else:
            return False
        
async def tripArrived(wk):
    """
    判断是否已到达目的地
    Whether arrived target location

    Args:
    - wk (WorkingMemory)

    Returns:
    - (bool): if True, has arrived, else not
    """
    now = wk.scheduler.now
    if now == None:
        return False
    elif now.type.value != ScheduleType.TRIP.value:
        return False
    else:
        if now.arrived:
            return True
        return False
    
async def routeFailed(wk):
    """
    判断导航是否失败
    Whether the route request failed

    Args:
    - wk (WorkingMemory)

    Returns:
    - (bool): if True, failed, else not
    """
    now = wk.scheduler.now
    if now == None or now.type.value != ScheduleType.TRIP.value:
        return False
    elif now.route_failed:
        wk._agent.Hub.Update([AgentMessage(wk._agent.Hub._agent_id, int(time.time()*1000), '抱歉, 当前行程导航请求失败, 已跳过该行程', None, None)])
        return True
    return False