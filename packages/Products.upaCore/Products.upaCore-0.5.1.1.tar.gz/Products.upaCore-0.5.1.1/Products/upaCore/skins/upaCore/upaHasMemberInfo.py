folder = context.portal_membership.getHomeFolder()
if folder is None:
    return False

mi = folder.getFolderContents(contentFilter=dict(portal_type='MemberInfo'))
return len(mi) > 0

