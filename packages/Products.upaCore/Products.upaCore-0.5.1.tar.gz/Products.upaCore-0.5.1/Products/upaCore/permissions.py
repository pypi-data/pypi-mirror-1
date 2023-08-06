# -*- coding: iso-8859-15 -*-

################################################################
# upaCore
#
# (C) 2008 
# ZOPYX Limited & Co. KG
# Charlottenstr. 37/1, D-72070 Tübingen, Germany
# info@zopyx.com, www.zopyx.com 
################################################################

from Products.CMFCore.permissions import setDefaultRoles

upacoreAddMemberInfo = 'upacore: Add MemberInfo'
upacoreViewInternally = 'upacore: View internally'

setDefaultRoles(upacoreAddMemberInfo, ('Manager', 'Member'))
setDefaultRoles(upacoreViewInternally, ('Manager', 'Member', 'Owner'))

# Maps portal_type to Add permissions

permissions = {
    'MemberInfo' : upacoreAddMemberInfo,
}
