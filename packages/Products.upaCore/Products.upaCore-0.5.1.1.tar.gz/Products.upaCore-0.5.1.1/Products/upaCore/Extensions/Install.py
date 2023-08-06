###########################################################################
# TextIndexNG V 3                
# The next generation TextIndex for Zope
#
# This software is governed by a license. See
# LICENSE.txt for the terms of this license.
###########################################################################


import transaction 
from StringIO import StringIO

from Products.CMFCore.utils import getToolByName
from Products.CMFCore.permissions import ManagePortal
from Products.CMFCore.DirectoryView import addDirectoryViews

def installProduct(installer, product):

    installer.installProduct(product)
    transaction.savepoint()

def install(self):                                       
    out = StringIO()

    installer = getToolByName(self, 'portal_quickinstaller')

    print >> out, "Successfully installed"  
    return out.getvalue()


def uninstall(self):                                       
    out = StringIO()

    print >> out, "Successfully uninstalled" 
    return out.getvalue()
