# Clean orphan member accounts (orphan=no member folder)

from Products.CMFCore.permissions import ManageUsers

portal = context.portal_url.getPortalObject()
member = context.portal_membership.getAuthenticatedMember()
if not member.checkPermission(ManageUsers, portal):
    raise Unauthorized('You are not allowed cleanup the member database')

mf = context.portal_url.getPortalObject().Members
uf = context.acl_users

for uid in uf.getUserNames():
    folder = getattr(mf, uid, None)
    have_index = folder and 'index_html' in folder.objectIds()
    print uid, folder, have_index
    if not folder:
        uf._doDelUsers([uid])
        print 'DELETED'

context.portal_memberdata.pruneMemberDataContents()
return printed

