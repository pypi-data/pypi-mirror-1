## Controller Script Python "validate_invite"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind state=state  
##bind subpath=traverse_subpath
##parameters=invite_to_address='',invitecode=None
##title=validates the email adresses

from Products.CMFCore.utils import getToolByName
reg_tool = getToolByName(context, 'portal_registration')

if not invite_to_address:
    state.setError('invite_to_address', 'Email address is a mandatory field.', 'email_required')

if invite_to_address and not reg_tool.isValidEmail(invite_to_address):
    state.setError('invite_to_address', 'Please submit a valid email address.', 'email_required')

if state.getErrors():
    state.set(status='failure', portal_status_message='Please correct the indicated errors test.')

return state
