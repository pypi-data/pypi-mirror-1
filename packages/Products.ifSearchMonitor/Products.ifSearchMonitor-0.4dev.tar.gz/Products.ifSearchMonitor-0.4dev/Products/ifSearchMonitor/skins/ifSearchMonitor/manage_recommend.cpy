## Script (Python) "manage_recommend"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind state=state
##bind subpath=traverse_subpath
##parameters=criteria, other='', recommended=[], rc_remove=[]
##title=Suggested results handler
##

save = context.REQUEST.get('form.button.save',None)
cancel = context.REQUEST.get('form.button.cancel',None)

if save:
    other = criteria + '\n' + other
    res = []

    if rc_remove:
        res = context.portal_catalog.searchResults(id=rc_remove)
    for r in res:
        obj = r.getObject()
        old_criteria = obj.getProperty('SuggestedCriteria')
        if old_criteria:
            new_criteria = list(old_criteria)
            new_criteria.remove(criteria)
            obj.manage_changeProperties(SuggestedCriteria=new_criteria)
        obj.reindexObject(idxs=['SuggestedCriteria'])

    res = []
    if recommended:
        res = context.portal_catalog.searchResults(id=recommended)
    for r in res:
        obj = r.getObject()
        if not obj.hasProperty('SuggestedCriteria'):
            obj.manage_addProperty('SuggestedCriteria', [], 'lines')
        obj.manage_changeProperties(SuggestedCriteria=other)
        obj.reindexObject(idxs=['SuggestedCriteria'])
    return state.set(portal_status_message='saved recommended results for ' + criteria)

if cancel:
    return state.set(portal_status_message='edit cancelled')
