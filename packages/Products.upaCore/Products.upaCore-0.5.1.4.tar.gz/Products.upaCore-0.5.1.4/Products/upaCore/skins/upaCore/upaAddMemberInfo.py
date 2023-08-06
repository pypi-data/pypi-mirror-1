## Script (Python) "upaAddMemberInfo"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind subpath=traverse_subpath
##parameters=username='', name='', email='', REQUEST=None
##title=Add upaMemberInfo
##

# create a MemberInfo object 'index_html' inside the memberfolder

if REQUEST is not None:
    return False

# handle plain zope account
if not(name and email):
    return False

firstname, lastname = name.split(' ',1)
email_private = email

portal = context.portal_url.getPortalObject()
try:
    member_folder = portal.Members[username]

    member_folder.invokeFactory('MemberInfo', 
                                id='index_html',
                                firstName=firstname,
                                lastName=lastname,
                                emailPrivate=email_private,
                                )
except:
    # no MemberInfo is created, portlet will inform the user
    pass

return True
