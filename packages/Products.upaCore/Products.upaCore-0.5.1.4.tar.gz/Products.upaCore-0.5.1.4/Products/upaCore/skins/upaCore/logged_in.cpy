## Controller Python Script "logged_in"
##bind container=container
##bind context=context
##bind namespace=
##bind script=script
##bind state=state
##bind subpath=traverse_subpath
##parameters=
##title=Initial post-login actions
##

# a customized version of portal_login/logged_in.py

from Products.CMFCore.utils import getToolByName
from Products.CMFPlone import PloneMessageFactory as _
REQUEST=context.REQUEST

membership_tool=getToolByName(context, 'portal_membership')
if membership_tool.isAnonymousUser():
    REQUEST.RESPONSE.expireCookie('__ac', path='/')
    context.plone_utils.addPortalMessage(_(u'Login failed. Both login name and password are case sensitive, check that caps lock is not enabled.'), 'error')
    return state.set(status='failure')

member = membership_tool.getAuthenticatedMember()
login_time = member.getProperty('login_time', '2000/01/01')
initial_login = int(str(login_time) == '2000/01/01')
state.set(initial_login=initial_login)

must_change_password = member.getProperty('must_change_password', 0)
state.set(must_change_password=must_change_password)

if initial_login:
    state.set(status='initial_login')
elif must_change_password:
    state.set(status='change_password')

membership_tool.loginUser(REQUEST)

# check for existing MemberInfo
member_folder = member.getHomeFolder()
member_info = member_folder.listFolderContents(contentFilter={"portal_type": "MemberInfo"})

# create and redirect to MemberInfo
if not(member_info):
    username = member.getId()
    fullname = member.getProperty('fullname','Vorname Nachname')
    email = member.getProperty('email','')
    if context.upaAddMemberInfo(username, fullname, email, REQUEST=None):
        return container.REQUEST.RESPONSE.redirect(member_folder.index_html.absolute_url())
    else:
        return container.REQUEST.RESPONSE.redirect(member_folder.absolute_url())

#redirect to MemberInfo
if member_info:
    return container.REQUEST.RESPONSE.redirect(member_info[0].absolute_url())
