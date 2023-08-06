## Controller Python Script "prefs_bannertool_set"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind state=state
##bind subpath=traverse_subpath
##parameters=RESPONSE=None
##title=
##

request=context.REQUEST

portal = context.portal_url.getPortalObject()
banner_tool = context.banner_tool

request.set('title', 'Banner Tool Settings')

# check for the delete button
delete = not request.get('form.button.delete', None) is None
if delete:
   banner_tool.manage_deleteSettings(request)
   return state.set(status='success', portal_status_message='Banner registry settings updated.')

banner_tool.manage_setRegistry(request)

return state.set(status='success', portal_status_message='Banner registry settings updated.')
