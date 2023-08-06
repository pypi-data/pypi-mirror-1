## Controller Python Script "send_invite_codes"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind state=state
##bind subpath=traverse_subpath
##parameters=users='', enforce=[], days=''
##title=validates the user invites page template

plone_invite = context.plone_invite

for user in users:
    num = user['num']
    userid = user['id']
    userenforce = userid in enforce
    if num:
        num = int(num)
        plone_invite.generateInvite(userid, num, userenforce)

if days:
    days = int(days)
    plone_invite.manage_changeProperties(days=days)
    
state.set(portal_status_message='Invites have been registered.')
return state
