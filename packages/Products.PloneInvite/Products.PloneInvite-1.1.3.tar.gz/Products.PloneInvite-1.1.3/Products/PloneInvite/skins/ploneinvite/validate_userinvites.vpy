## Controller Python Script "validate_userinvites"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind state=state
##bind subpath=traverse_subpath
##parameters=users='', enforce=[], days=''
##title=validates the user invites page template

try:
    if days:
        days = int(days)
except ValueError:
    state.setError('days',
                   'Please enter an integer for number days',
                   'invalid_days')

for user in users:
    num = user['num']
    try:
        if num:
            num = int(num)
    except ValueError:
        state.setError('invites',
                       'Please enter an integer for number of invites',
                       'invalid_invites')
        
if state.getErrors():
    state.set(status='failure', portal_status_message='Please correct the indicated errors.')
else:
    state.set(portal_status_message='Invites have been registered.')

return state
