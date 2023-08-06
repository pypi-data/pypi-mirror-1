## Controller Python Script "bibfolder_flex_view_settings_addmask"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind state=state
##bind subpath=traverse_subpath
##parameters=
##title=Reconfigure the bibflexview Tool


req=context.REQUEST

context.portal_bibliography_flexible_view.copy_tool_properties(context)
context.portal_bibliography_flexible_view.add_mask(context)

return state.set()
