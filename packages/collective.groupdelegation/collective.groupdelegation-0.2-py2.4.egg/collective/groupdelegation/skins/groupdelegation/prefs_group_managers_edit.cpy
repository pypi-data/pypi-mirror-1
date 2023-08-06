## Script (Python) "prefs_group_edit"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=groupname='', add=[], delete=[]
##title=Edit user
##
from Products.PythonScripts.standard import url_quote
group=context.portal_groups.getGroupById(groupname)

groupManagers = list(group.getProperty('delegated_group_member_managers', ()) or ())

REQUEST=context.REQUEST
msg = 'No change has been done.'

for u in add:
    msg = '%s managers added.' %len(add)
    if u not in groupManagers:
        groupManagers.append(u)

for u in delete:
    msg = '%s managers removed.' %len(delete)
    if u in groupManagers:
        groupManagers.remove(u)
    
    
groupManagers = tuple(groupManagers)     
    
group.setGroupProperties({'delegated_group_member_managers' : groupManagers})

url='%s?groupname=%s&portal_status_message=%s' % (context.prefs_group_managers.absolute_url(),
                                                  groupname,
                                                  url_quote(msg))

return REQUEST.RESPONSE.redirect(url)
