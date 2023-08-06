################################################################
# ubCore
#
# (C) 2008 
# ZOPYX Limited & Co. KG
# Charlottenstr. 37/1, D-72070 Tübingen, Germany
# info@zopyx.com, www.zopyx.com 
################################################################

import os, sys

if __name__ == '__main__':
    execfile(os.path.join(sys.path[0], 'framework.py'))

from zope.component import getMultiAdapter
from AccessControl import Unauthorized
from Testing import ZopeTestCase
from Products.PloneTestCase.PloneTestCase import PloneTestCase, setupPloneSite, installProduct

installProduct('ubCore')
installProduct('LinguaPlone')
installProduct('Scrawl')
installProduct('Reflecto')
installProduct('ATVocabularyManager')
#installProduct('TextIndexNG3')

setupPloneSite(extension_profiles=('Products.ubCore:ubCore.default', ))

class TestInstallation(PloneTestCase):
    '''Test the various content types'''

    def afterSetUp(self):
        pass

    def testBlogEntry(self):
        self.login('gott')
        portal = self.portal
        # Standard blog entry can be created everywhere
        portal.invokeFactory('Blog Entry', 'blogentry')

        # now a blog folder
        portal.invokeFactory('BlogFolder', 'blog')
        blog = portal.blog
        blog.invokeFactory('Blog Entry', 'entry1')
        blog.invokeFactory('Blog Entry', 'entry2')
        blog.invokeFactory('Topic', 'aggregator')

        # this fails since we allow only Blog Entries
        self.assertRaises(ValueError, blog.invokeFactory, 'Page', 'page1')


    def testVocabularies(self):
        self.login('gott')
        ids = self.portal.portal_vocabularies.objectIds()
        self.assertEqual('audience' in ids, True)
        self.assertEqual('news_remote_servers' in ids, True)


    def testRelecto(self):
        self.login('gott')
        self.portal.invokeFactory('Reflector', 'reflector')


    def testAudience(self):
        self.login('gott')
        self.portal.invokeFactory('Document', 'doc')
        doc = self.portal.doc
        doc.getField('audience').getMutator(doc)(('alumni',))
        doc.view()


    def testAudienceManager(self):
        from Testing.makerequest import makerequest
        REQUEST = makerequest(self.app).REQUEST
    
        self.login('am')
        self.setRoles(('AudienceManager',))
        member = self.portal.portal_membership.getAuthenticatedMember()
        self.assertEqual('AudienceManager' in member.getRoles(), True)
        view = getMultiAdapter((self.portal, REQUEST), name='controlpanel-audience')
        result = view()

        self.logout()
        self.login('joe')
        member = self.portal.portal_membership.getAuthenticatedMember()
        view = getMultiAdapter((self.portal, REQUEST), name='controlpanel-audience')
        self.assertRaises(Unauthorized, view)



def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestInstallation))
    return suite

if __name__ == '__main__':
    framework()
