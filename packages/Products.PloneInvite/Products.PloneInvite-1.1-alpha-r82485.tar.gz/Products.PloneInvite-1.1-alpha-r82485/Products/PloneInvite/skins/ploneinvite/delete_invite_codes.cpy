## Controller Python Script "delete_invite_codes"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind state=state
##bind subpath=traverse_subpath
##parameters=delete=[]
##title=validates the user invites page template

plone_invite = context.plone_invite

delInvite = plone_invite.delInvite

for invitecode in delete:
    delInvite(invitecode)
    
state.set(portal_status_message='%d invites have been deleted.'%len(delete))
return state
