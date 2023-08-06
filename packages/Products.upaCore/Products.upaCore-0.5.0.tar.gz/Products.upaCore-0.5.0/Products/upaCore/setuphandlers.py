"""
CMFPlone setup handlers.
"""

import os

from Products.CMFCore.utils import getToolByName
from config import PROJECTNAME

class PloneGenerator:

    def installProducts(self, p):
        """QuickInstaller install of required Products"""
        qi = getToolByName(p, 'portal_quickinstaller')
        qi.installProduct('PloneFormGen')
        qi.installProduct('FCKeditor')
        qi.installProduct('Reflecto')

    def setupMembers(self, p):
        for method in (p.portal_membership.addMember, p.acl_users.userFolderEditUser):
            method('gott', 'gott', ('Member', 'Manager'), '')
            method('joe', 'joe', ('Member', ), '')


def importVarious(context):
    """ """

    if context.readDataFile('upacore_various.txt') is None:
        return

    site = context.getSite()
    gen = PloneGenerator()
    gen.installProducts(site)
    gen.setupMembers(site)
