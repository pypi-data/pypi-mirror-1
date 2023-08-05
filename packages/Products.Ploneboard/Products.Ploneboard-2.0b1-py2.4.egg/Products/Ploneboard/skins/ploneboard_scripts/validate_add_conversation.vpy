## Controller Validator "validate_add_conversation"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind state=state
##bind subpath=traverse_subpath
##parameters=
##title=Validates a posting
# $Id: validate_add_conversation.vpy 54617 2007-11-28 13:16:22Z wichert $

from Products.CMFCore.utils import getToolByName
from Products.CMFPlone import PloneMessageFactory as _

putils = getToolByName(context, 'plone_utils')

title = context.REQUEST.get('title', '');

if len(title) <= 0:
    state.setError("title", "No title entered", new_status="failure")

if state.getErrors():
    message = _(u'Please correct the indicated errors.')
    putils.addPortalMessage(message)

return state
