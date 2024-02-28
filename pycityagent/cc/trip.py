async def whetherTripArrived(wk):
    '''是否到达目的地'''
    reason = wk.Reason
    if reason['tripArrived']:
        return True
    return False

async def whetherRouteFailed(wk):
    '''是否到达目的地'''
    reason = wk.Reason
    if reason['routeFailed']:
        return True
    return False