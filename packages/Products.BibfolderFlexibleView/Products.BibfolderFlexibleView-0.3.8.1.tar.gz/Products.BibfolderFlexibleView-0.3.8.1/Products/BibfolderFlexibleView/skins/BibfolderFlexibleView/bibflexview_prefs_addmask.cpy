## Controller Python Script "bibflexview_prefs_addmask"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind state=state
##bind subpath=traverse_subpath
##parameters=
##title=Reconfigure the bibflexview Tool


req=context.REQUEST

context.portal_bibliography_flexible_view.add_mask(context.portal_bibliography_flexible_view)

return state.set()
