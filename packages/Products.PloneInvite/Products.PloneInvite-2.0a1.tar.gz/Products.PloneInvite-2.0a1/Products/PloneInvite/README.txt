..  This text is intended to be rendered in a pretty way in Plone's "Add-on
    products configuration" (prefs_install_products_form).  The targeted
    audience is the site manager who wants to get it running quick, and who may
    want to look up things here.  The format is Restructured Text:
    http://docutils.sourceforge.net/docs/user/rst/quickref.html 


About PloneInvite
=================

PloneInvite is a tool for Plone which allows portal members to invite new users
to register into the portal. Members get invite codes which are used to send
the invitation. 

This is a short introduction. 
For more information, bug trackers, feauture request, etcetera, see the
`product web page`_.

.. _`product web page`: http://plone.org/products/plone-invite


How to Use
==========

For the portal administrator:
-----------------------------

1.  Go to Site Setup and click on the "Member Invitations" link.

2.  On this page you can give invites to other users and set the expiration 
    period in days for the portal invites.

For a member:
-------------

1.  After logging in, open the "invite someone" link available under your login
    name in the upper right corner.

2.  This page allows members to send invitations as well as see the status of
    their invitations.

   
Install
=======

1.  Add Products.PloneInvite to your buildout's instance's eggs.

2.  Install the product from Plone's `Add-on configuration`_, or use the 
    portal_quickinstaller in the ZMI.


Features
========

1.  Assign invitations to the current site members. 
    With these invitations, they can invite new members. 
    New members will receive this invitation by e-mail.

2.  The site manager can enforce email in the the invitation.
    This means the invitee must register with the email address to which the 
    invitation was sent.

3.  The inviting member can optionally also enforce email, 
    if it was not already enforced by the site manager.

4.  The "@@register" form now contains a field "invite_code". 
    New users can register only if they have a valid invitation code.

5.  The invitation e-mail message can be customized. 
    (This can be done through the ZMI, it's a skin template.)

6.  The portal administrator manage invitations through the `configlet`_:



    - see which invitations have been accepted

    - revoke unused invitations
     
    - revoke sent but unaccepted invitations



Configuration
=============
              
1.  Customize PloneInvite/skins/invite_template.cpt in your Product folder to 
    customize your portal Invitation template.

2.  The email address which will be used as the "sender" in invite e-mails is 
    the site-wide e-mail address. You can change it via the site's 
    `Mail configuration`_.


Requirements
============

Tested on:

- Plone 4.0a3, Zope 2.12.2


Technical summary
=================

-   Subclasses and overrides plone.app.users' RegistrationForm ("@@register")
-   Stores invitations in a portal tool ('portal_invitations')
-   Uses skin templates and scripts for sending and managing invitations
-   Defines custom permissions (among others, for giving invitations to
    members)


Caveats
=======

This product has not been tested in conjunction with other products, such
as emaillogin or membrane users.


Credits
=======

-   Created by Giovani Spagnolo of Partecs Participatory Technologies.
-   Plone 4 port and maintained by Kees Hink of 
    Goldmund, Wyldebeast & Wunderliebe.

.. _`configlet`: ../user_invites
.. _`Mail configuration`: ../@@mail-controlpanel
.. _`Add-on configuration`: prefs_install_products_form
