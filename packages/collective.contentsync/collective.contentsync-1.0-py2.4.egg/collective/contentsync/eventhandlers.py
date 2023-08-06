def onSynchronizeStateChange(state, event):
    if state.view is None:
        return

    response = state.view.request.RESPONSE
    if state.initializing:
        response.write(str(state.view()))
        response.write('<input style="display: none;" name="contentSyncLabel" value="">')

    response.write('<input style="display: none;" name="contentSyncStep" value="%s">' % state.step)   
    response.write('<input style="display: none;" name="contentSyncTotal" value="%s">' % state.total)
    response.write('<input style="display: none;" name="contentSyncProgress" value="%s">' % state.index)
    if state.target is not None:
        response.write('<input style="display: none;" name="contentSyncLabel" value="%s">' % state.target.title_or_id())        
    if state.message:
        response.write('<input style="display: none;" name="contentSyncLog" value="%s">' % state.message) 

    if state.done:
        # todo: translation
        response.write('<input style="display: none;" name="contentSyncLabel" value="%s">' % 'Synchronization complete')
