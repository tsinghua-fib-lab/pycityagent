async def whetherUserControl(wk):
    reason = wk.Reason
    if reason['hasUserControl']:
        return True
    else:
        return False
    
async def whetherEndControl(wk):
    reason = wk.Reason
    if reason['endUserControl']:
        return True
    else:
        return False