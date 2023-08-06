PloneInvite

   PloneInvite is a tool for Plone which allows portal members to invite new
   users to register into the portal. The portal administrator assigns the
   invite codes to the portal members and members can and  these invite codes
   are used to send the invitation. 


How to Use

    For Portal Administrator:

    1.  Log in as portal administrator, go to Site Setup and click on Member
        Invitations link.

    2.  On this page you can give invites to other users and set the expiration
        period in days for the portal invites.

    For Member:

    1. After logging in open invite link present just below search box.

    2. This page allows members to send invitations as well as see the status of
       their invitations.

   
Install

    1  Put this product in to products folder and restart the zope.

    2  Install the product from portal_quickinstaller.


Features

    1  Assign invites to the users.

    2  Admin can enforce email in the the invitation (invitee register with the
    same email address to which the invitation was sent )

    3  Expiry Date for the invitation

    4  Inviter can enforce email

    5  User can register only if they have the invitation code

    6  Manager can add users with out invitation code

    7  Invitation e-mail message can be customized (page template modification)


Configuration
              
    Customizing the invite e-mail

        * Go to the ZMI
        
        * Go to portal_skins, to plone_invite, select the
          invite_template, customize it

    Customizing the invitation sender address
    
        The email address which will be used as the "sender" in invite e-mails
        is the site-wide e-mail address by default. You can change it via
        "@@mail-controlpanel".

        If you want to use a different sender address than the site address:
            
            * Go to the ZMI

            * Go to the plone_invite tool, go to the 'properties' tab, modify
              plone_invite_email_address


Requirements

    Tested on:
    
    - Plone 3.2.1, CMF 2.1.2, Zope 2.10.6-final

    - Plone 3.3b1, CMF 2.1.2, Zope 2.10.7-final

    - Plone 3.3.3, CMF 2.1.2, Zope 2.10.9-final


Warning
    
    The product relies on a modification of the join_form for its
    functionality. Using the product alongside another product which also
    modifies join_form will not work.


Credits

    Created by Giovani Spagnolo of Partecs Participatory Technologies.
    Maintained by Kees Hink of Goldmund, Wyldebeast & Wunderliebe.
