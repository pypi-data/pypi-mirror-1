Group Delegation
================

A customization of some Plone Groups Management screens, and some new templates
and scripts added, providing the delegation of Groups management in Plone for any
member without 'Manager' role.

This code was originally published by Ingeniweb in Grufspaces product and has been
upgraded for plone3.x compliance, some tests have also been added.

How to use this product :

* add collective.groupdelegation to your buildout (see docs/INSTALL.txt for more information)

* Intall "Group Delegation" in your plone site using portal_quickinstaller

* Go to Users/Groups management control panels,  Create a group and some users.

* Choose the group you want to delegate management

* Click on "Group Managers" tab

* Search for, and choose the user you want delegate the group management to.

* Connect to your site with this user credentials

* A "My groups" tab will appear in personal tools, click on this link

* The group will appear in list 

* Click on this group link, now you can manage it without Manager rights.


TODO : Security issues
----------------------

At this time no special zope security or role is needed to manage groups in Plone. The
process is only protected by a condition "chekPermission('Manage portal')"" inside
templates.

This product is following the same logic, it's just a skin product ,
the only thing done to allow/disallow groups management is a new property added to groups.

To improve security it could be useful to add a new specific zope security
"Manage groups", only allowed to a "Group manager" new role.

Then, when choosing the group manager, could it be possible to allow/disallow the local role 
to a specific user on a specific group ? i don't know.

TODO : template and python scripts redesign
-------------------------------------------

At this time this product is using actual Plone groups management templates and scripts because
it is using the same methods to search/add/remove groups members, redesigning
this product would mean first a complete redesign of plone templates, a big work that could
be done in future ... 


For more information read the doctest (readme.txt) inside product.
