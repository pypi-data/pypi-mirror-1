## Controller Python Script "bibfolder_flex_view_settings_delcategory"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind state=state
##bind subpath=traverse_subpath
##parameters=
##title=Reconfigure the bibflexview Tool


req=context.REQUEST

context.portal_bibliography_flexible_view.delete_mask(context, req['unparsed_mask_checks'])

return state.set()
