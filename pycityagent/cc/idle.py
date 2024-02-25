async def whetherGoTrip(wk):
    '''判断是否可以开始出行'''
    reason = wk.Reason
    if reason['startTrip']:
        return True
    return False

async def whetherGoShop(wk):
    '''判断是否可以开始购物'''
    reason = wk.Reason
    if reason['startShop']:
        return True
    return False

async def whetherGoConverse(wk):
    '''判断是否开始对话'''
    reason = wk.Reason
    if reason['startConve']:
        return True
    return False