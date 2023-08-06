from elementtree import ElementTree as ET

import md5
import urllib

from Products.CMFPlone.tests import PloneTestCase

class TestMindMeisterAPI(PloneTestCase.PloneTestCase):
    # Please don't abuse, this is for testing purposes only!
    api_key = '548b880ab948df669367a24a1e51ccd2' 
    secret = '3f1f2a6eff01225e'
    mindmeister_url = 'http://www.mindmeister.com/services/rest/'
    
    def test_null(self):
        parms = {
            'method': 'mm.test.null',
            'api_key': self.api_key, 
            }
        pl = [self.secret] + sorted([''.join(t) for t in parms.items()])
        api_sig = md5.new(''.join(pl)).hexdigest()
        parms['api_sig'] = api_sig

        parms_url = urllib.urlencode(parms)
        url = '%s?%s' % (self.mindmeister_url, parms_url)
        fp = urllib.urlopen(url)
        xml = fp.read()

        tree = ET.fromstring(xml)
        status = tree.get('stat')
        self.assertEquals(status, 'ok')

    def test_echo(self):
        to_echo = 'slc.mindmap test'
        parms = {
            'method': 'mm.test.echo',
            'api_key': self.api_key, 
            'value': to_echo,
            }

        parms_url = urllib.urlencode(parms)
        url = '%s?%s' % (self.mindmeister_url, parms_url)
        fp = urllib.urlopen(url)
        xml = fp.read()

        tree = ET.fromstring(xml)
        status = tree.get('stat')
        self.assertEquals(status, 'ok')
        echo = tree.getiterator().pop().text
        self.assertEquals(echo, to_echo)


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestMindMeisterAPI))
    return suite


