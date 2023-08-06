################################################################
# upaCore
#
# (C) 2008 
# ZOPYX Limited & Co. KG
# Charlottenstr. 37/1, D-72070 Tübingen, Germany
# info@zopyx.com, www.zopyx.com 
################################################################

from Products.CMFCore.DirectoryView import registerDirectory
from Products.Archetypes.public import process_types, listTypes

from config import PROJECTNAME

registerDirectory('skins', globals())

def initialize(context):
    from content import memberinfo

    content_types, constructors, ftis = process_types(
        listTypes(PROJECTNAME),
        PROJECTNAME)

    # Assign an own permission to all content types
    # Heavily based on Bricolite's code from Ben Saller
    from permissions import permissions

    from Products.CMFCore.utils import ContentInit
    allTypes = zip(content_types, constructors)

    for atype, constructor in allTypes:
        kind = "%s: %s" % (PROJECTNAME, atype.archetype_name)
        ContentInit(
            kind,
            content_types      = (atype,),
            permission         = permissions[atype.portal_type],
            extra_constructors = (constructor,),
            fti                = ftis,
            ).initialize(context)
