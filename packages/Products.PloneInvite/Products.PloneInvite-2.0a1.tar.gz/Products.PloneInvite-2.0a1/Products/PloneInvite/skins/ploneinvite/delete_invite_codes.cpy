## Controller Python Script "delete_invite_codes"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind state=state
##bind subpath=traverse_subpath
##parameters=delete=[]
##title=validates the user invites page template

portal_invitations = context.portal_invitations

delInvite = portal_invitations.delInvite

for invitecode in delete:
    delInvite(invitecode)
    
state.set(portal_status_message='%d invites have been deleted.'%len(delete))
return state
