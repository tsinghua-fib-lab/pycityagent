async def whetherShopFinished(wk):
    '''是否结束购物'''
    reason = wk.Reason
    if reason['endShop']:
        return True
    return False