## This library is free software; you can redistribute it and/or
## modify it under the terms of the GNU  General Public
## License as published by the Free Software Foundation; either
## version 2 of the License, or any later version.

## This library is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
##  General Public License for more details.

## You should have received a copy of the GNU  General Public
## License along with this library; if not, write to the Free Software
## Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA

from Products.CMFCore import permissions as CMFCorePermissions
from AccessControl.SecurityInfo import ModuleSecurityInfo
from Products.CMFCore.permissions import setDefaultRoles

security = ModuleSecurityInfo('Products.PloneInvite')

# Assign invites to others
security.declarePublic('GeneratePortalInvites')
GeneratePortalInvites = 'PloneInvite: Generate Portal Invites' 
setDefaultRoles(GeneratePortalInvites, ())
# Invite other users
security.declarePublic('InvitePortalUsers')
InvitePortalUsers = 'PloneInvite: Invite Portal Users' 
setDefaultRoles(InvitePortalUsers, ())
# Manage your own invites
security.declarePublic('ManageMemberInvites')
ManageMemberInvites = 'PloneInvite: Manage Member Invites' 
setDefaultRoles(ManageMemberInvites, ())

ManagePortalInvites = CMFCorePermissions.ManagePortal
AddPortalUser = CMFCorePermissions.AddPortalMember
