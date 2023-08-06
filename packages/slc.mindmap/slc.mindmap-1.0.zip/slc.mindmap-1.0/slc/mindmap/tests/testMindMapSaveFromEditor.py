import os
import cookielib
import urllib2

from Products.CMFPlone.tests import PloneTestCase
from Products.CMFPlone.tests import dummy

from slc.mindmap.browser.mindmap import MultipartPostHandler
from slc.mindmap.browser.mindmap import SaveMindMap


class TestMindMapSaveFromEditor(PloneTestCase.PloneTestCase):
    """ Test browser.mindmap.SaveMindMap class that is called by MindMeister.com 
        when a file is saved through the editor.
    """

    def afterSetUp(self):
        self.portal.acl_users._doAddUser('user1', 'secret', ['Member'], [])
        self.membership = self.portal.portal_membership
        self.createMemberarea('user1')
        self.workflow = self.portal.portal_workflow
        self.setupAuthenticator()

    def testMindMapSave(self):
        """ """
        portal = self.getPortal()

        # Create new Mindmap file in ZODB
        self.folder.invokeFactory('File', id='mindmap')
        mindmap = self.folder.mindmap
        file = open('%s/parts/omelette/slc/mindmap/tests/Plone_API.mmap' % os.getcwd())
        mindmap.setFile(file)

        cookies = cookielib.CookieJar()
        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cookies),
                                    MultipartPostHandler)

        fields = {
            'file[id]':  'Plone_API.map',
            'file[name]': 'Plone_API.map',
            'file[content]': open('%s/parts/omelette/slc/mindmap/tests/empty.mmap' % os.getcwd()), 
            }

        old_size = self.folder.mindmap.getFile().size
        SaveMindMap(mindmap, fields)()
        new_size = self.folder.mindmap.getFile().size
        self.failIf(new_size == old_size)


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestMindMapSaveFromEditor))
    return suite

