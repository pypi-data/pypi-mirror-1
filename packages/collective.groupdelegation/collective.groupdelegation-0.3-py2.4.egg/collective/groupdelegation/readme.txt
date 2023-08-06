Group Delegation doctests
=========================

This product allows simple plone members to manage some groups.
It overloads some plone groups forms to add a new property ('delegated_group_member_managers')
If some group has a memberId set in this property, this member can manage its members.

In this file we don't test the plone form skin overloads. I hope nothing has been broken.
This overload was necessary for two reasons :

- harcoded contentViews in user/groups management forms (a tab has been added, so it was necessary)

- a small bug in pref_group_details.cpt template when adding list types properties to groups ('delegated_group_member_managers')

We just test :

- the product installation and the new property added to groups,

- the delegated management forms added in this product using testbrowser

TODO :

- Test the prefs_group_managers.cpt template


Install Group Delegation    

    >>> from Products.CMFCore.utils import getToolByName
    >>> portal_setup = getToolByName(self.portal, 'portal_setup')
    >>> _ = portal_setup.runAllImportStepsFromProfile('profile-collective.groupdelegation:default')   
    

Open a test browser session (used below)

    >>> from Products.Five.testbrowser import Browser
    >>> browser = Browser()
    >>> browser.open('http://nohost/plone/')
    
Create a group with two users inside
    
    >>> groups = self.portal.portal_groups
    >>> groups.addGroup('foo', [], [])    
    True
    >>> aclusers = self.portal.acl_users
    >>> aclusers._doAddUser('user1', 'secret', ['Member'], [], ['foo'])
    >>> aclusers._doAddUser('user2', 'secret', ['Member'], [], ['foo'])
    
Control if foo has the new property installed by collective.groupdelegation    

    >>> foo = groups.getGroupById('foo')
    >>> 'delegated_group_member_managers' in foo.propertyIds()
    True
    

Create another user and set it as Group manager for 'foo'

    >>> aclusers._doAddUser('user3', 'secret', ['Member'], [], [])    
    >>> foo.setGroupProperties({'delegated_group_member_managers' : ('user3',)})
    >>> foo.getProperty('delegated_group_member_managers')
    ('user3',)
    

Login as user3

    >>> browser.getLink('Home').click()
    >>> browser.getLink('Log in').click()
    >>> browser.getControl('Login Name').value = 'user3'
    >>> browser.getControl('Password').value = 'secret'
    >>> browser.getControl('Log in').click()
    >>> "You are now logged in" in browser.contents
    True

Test action 'My groups'    
 
    >>> "My groups" in browser.contents
    True
    
Go to "My groups" page which list all groups that user3 can manage  
  
    >>> browser.getLink('My groups').click()
    >>> browser.url
    'http://nohost/plone/prefs_deleg_groups_overview'
    
See if 'foo' is in the list of groups
    
    >>> 'foo' in browser.contents
    True
    
Click on 'foo' and go to the 'foo' management delegated page

    >>> browser.getLink('foo').click()
    >>> browser.url
    'http://nohost/plone/prefs_deleg_group_members?groupname=foo'
       
Try to see if 'user1' and 'user2' are listed as members of 'foo' (they must appear in delete list)
 
    >>> ctrl = browser.getControl(name='delete:list')
    >>> ctrl.options
    ['user1', 'user2']
    
Remove user1 from group    

    >>> ctrl.value=['user1']
    >>> browser.getControl(name='form.button.Edit').click()
    >>> browser.url
    'http://nohost/plone/prefs_deleg_group_members'
    >>> ctrl = browser.getControl(name='delete:list')
    >>> ctrl.options
    ['user2']
    
Control foo members now
   
    >>> [m.getId() for m in foo.getGroupMembers()]
    ['user2']

    
user3 search for himself as member to add in foo    

but in first time we must set a fullname to user3 otherwise
plone3 searchUsers will not work (plone3 bug ?)

    >>> u3 = aclusers.getUserById('user3')
    >>> self.portal.plone_utils.setMemberProperties(u3, fullname='user3')
    
    >>> browser.getControl(name='searchstring').value='user3'
    >>> browser.getControl(name='form.button.Search').click()
    >>> browser.url
    'http://nohost/plone/prefs_deleg_group_members'    
    
user3 add himself as groupmember in foo      

    >>> addctrl = browser.getControl(name='add:list')
    >>> addctrl.value = ['user3']
    >>> browser.getControl(name='form.button.Add').click()
    >>> browser.url
    'http://nohost/plone/prefs_deleg_group_members'
    >>> ctrl = browser.getControl(name='delete:list')
    >>> ctrl.options
    ['user2', 'user3']        
    
Control foo members finally
   
    >>> [m.getId() for m in foo.getGroupMembers()]
    ['user2', 'user3']    
    
Login as user1 and try to manage foo without rights

    >>> browser.reload()
    >>> browser.getLink('Log out').click()    
    >>> browser.getLink('Home').click()
    >>> browser.getLink('Log in').click()
    >>> browser.getControl('Login Name').value = 'user1'
    >>> browser.getControl('Password').value = 'secret'
    >>> browser.getControl('Log in').click()
    >>> browser.open('http://nohost/plone/prefs_deleg_group_members?groupname=foo')
    >>> 'You are not allowed to manage this group' in browser.contents
    True
    
    
    