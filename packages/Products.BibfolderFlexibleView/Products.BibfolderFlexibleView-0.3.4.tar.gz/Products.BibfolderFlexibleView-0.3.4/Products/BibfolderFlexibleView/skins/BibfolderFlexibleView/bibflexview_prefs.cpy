## Controller Python Script "bibflexview_prefs"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind state=state
##bind subpath=traverse_subpath
##parameters=
##title=Reconfigure the bibflexview Tool

req=context.REQUEST
bfvtool = context.portal_bibliography_flexible_view

bfvtool.manage_changeProperties(req)
bfvtool.process_masks(bfvtool, req)

return state.set(portal_status_message='Updated')
