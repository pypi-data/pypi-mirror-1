import binascii
import unittest
import urllib
from elementtree import ElementTree as ET

from zope.testing import doctestunit
from zope.component import testing
from Testing import ZopeTestCase as ztc

from Products.Five import zcml
from Products.Five import fiveconfigure
from Products.PloneTestCase import PloneTestCase as ptc
from Products.PloneTestCase.layer import PloneSite
ptc.setupPloneSite()

import slc.mindmap

class TestCase(ptc.PloneTestCase):

    class layer(PloneSite):
        @classmethod
        def setUp(cls):
            fiveconfigure.debug_mode = True
            zcml.load_config('configure.zcml',
                             slc.mindmap)
            fiveconfigure.debug_mode = False

        @classmethod
        def tearDown(cls):
            pass

    def test_mindmeister_api(self):
        TestMindMeisterAPI()

def test_suite():
    suite = unittest.TestSuite([
        # Unit tests
        #doctestunit.DocFileSuite(
        #    'README.txt', package='slc.mindmap',
        #    setUp=testing.setUp, tearDown=testing.tearDown),

        doctestunit.DocTestSuite(
            module='slc.mindmap.descriptors',
            setUp=testing.setUp, tearDown=testing.tearDown),

        # Integration tests that use PloneTestCase
        #ztc.ZopeDocFileSuite(
        #    'README.txt', package='slc.mindmap',
        #    test_class=TestCase),

        #ztc.FunctionalDocFileSuite(
        #    'browser.txt', package='slc.mindmap',
        #    test_class=TestCase),
        ])
    return suite

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')

