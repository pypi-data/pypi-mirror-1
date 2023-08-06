## Script (Python) "get_delegated_groups"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=
##title=Get delegated groups
##

from Products.CMFCore.utils import getToolByName
mtool = getToolByName(context, 'portal_membership')
member = mtool.getAuthenticatedMember()
member_id = member.getId()

delegated_groups=[]
search_view = context.restrictedTraverse('@@pas_search')
groups = search_view.searchGroups()
for group_info in groups:
   group = context.acl_users.getGroupById(group_info['groupid'])
   delegated_group_member_managers = group.getProperty('delegated_group_member_managers', ()) or ()
   if member_id in delegated_group_member_managers :
        delegated_groups.append(group)
return delegated_groups

