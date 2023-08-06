from plone.theme.interfaces import IDefaultPloneLayer
from zope.interface import Interface
from zope import schema
from Products.PloneInvite import PloneInviteMessageFactory as _

class IPloneInvitePolicy(IDefaultPloneLayer):
    """ A marker interface for the theme layer """

class IInviteCodeSchema(Interface):
    """ Schema definition for 'invite_code' field
    """ 
    invite_code = schema.TextLine(
        title=_(u'label_invite_code', default=u"Invitation code"),
        description=_(u'description_invite_code', 
            default=u"Enter the code you received to register."),
        required=True,
        )
