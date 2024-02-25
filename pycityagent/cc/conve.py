async def whetherStopConverse(wk):
    '''是否结束对话'''
    reason = wk.Reason
    if reason['endConve']:
        return True
    return False