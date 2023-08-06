## Controller Validator "prefs_bannertool_validate"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind state=state
##bind subpath=traverse_subpath
##parameters=
##title=Validates banner tool settings
##

from Products.CMFCore.utils import getToolByName
portal_url = getToolByName(context, 'portal_url')
portal = portal_url.getPortalObject()

# TODO: add validation here; e.g. whether path exisits in the site

# No errors.  Always make sure to return the ControllerState object
return state
