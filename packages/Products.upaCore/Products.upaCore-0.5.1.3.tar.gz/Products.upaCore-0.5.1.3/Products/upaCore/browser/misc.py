################################################################
# upaCore
#
# (C) 2008 
# ZOPYX Limited & Co. KG
# Charlottenstr. 37/1, D-72070 Tübingen, Germany
# info@zopyx.com, www.zopyx.com 
################################################################


from Globals import InitializeClass
from Products.Five import BrowserView
from Products.CMFCore.utils import getToolByName

class MiscView(BrowserView):
    """ helper code for managing the audience """

    def getFieldValue(self, fieldname):
        """ Return the value of a field for the current context object.
            Basically a convinience method for content types with
            an extended schema.
        """

        return self.context.getField(fieldname).getAccessor(self.context)()

    def setFieldValue(self, fieldname, value):
        """ Set the value of a field for the current context object.
            Basically a convinience method for content types with
            an extended schema.
        """

        return self.context.getField(fieldname).getMutator(self.context)(value)


InitializeClass(MiscView)
