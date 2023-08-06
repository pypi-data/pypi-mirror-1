from plone.app.users.browser.register import RegistrationForm
from zope.formlib import form
from Products.CMFPlone import PloneMessageFactory as _
from Products.PloneInvite.interfaces import IInviteCodeSchema
from Products.CMFCore.utils import getToolByName
from zope.app.form.interfaces import WidgetInputError

class InviteRegistrationForm(RegistrationForm):
    """ 
    Augument the standard registration form:
    - add field 'invite_code' to form_fields
    - modify validate_registration so it checks the code
    """

    description = u"Register using your invitation code."

    @property
    def form_fields(self):
        """ Append the extra 'invite_code' field  """
        defaultFields = super(InviteRegistrationForm, self).form_fields
        inviteFields = form.Fields(IInviteCodeSchema)
        return defaultFields + inviteFields

    @form.action(_(u'label_register', default=u'Register'),
                 validator='validate_invited_registration', name=u'register')
    def action_join(self, action, data):
        result = self.handle_join_success(data)
        return self.context.unrestrictedTraverse('registered')()

    def validate_invited_registration(self, action, data):
        """ Business logic for processing the invitation code """
        # First, call the regular validator
        errors = self.validate_registration(action, data)
        if errors:
            return errors

        # Now for the invitation code checks
        invite_code = self.widgets['invite_code'].getInputValue()
        username = self.widgets['username'].getInputValue()
        email = self.widgets['email'].getInputValue()
        portal_invitations = getToolByName(self, 'portal_invitations')
        invites = portal_invitations.invites
        invite = invites.get(invite_code, None)
        if invite is None or invite.used:
            err_str = _(u"invite_invalid", 
                default=u"Invite code does not exist or has already been used.")
            errors.append(WidgetInputError(
                'invite_code',u'label_invite_code',err_str))
            self.widgets['invite_code'].error = err_str
            return errors
        # Check if e-mail address matches (if this should be enforced).
        if invite.enforce_address and invite.sent_address!=email:
            err_str = _(u"invalid_email", 
                default=u"Please use the email address with which you have received your invitation.")
            errors.append(WidgetInputError(
                'email',u'label_email',err_str))
            self.widgets['email'].error = err_str
            return errors
        # If there are no errors, mark the invitation as used.
        invite.useInvite(invite_code, username)
        return errors
        
           
