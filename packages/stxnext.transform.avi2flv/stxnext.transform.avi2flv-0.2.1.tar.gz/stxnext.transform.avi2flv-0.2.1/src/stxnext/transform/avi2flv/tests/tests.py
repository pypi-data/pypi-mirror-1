import unittest

from zope.testing import doctestunit
from zope.component import testing
from Testing import ZopeTestCase as ztc

from Products.Five import zcml
from Products.Five import fiveconfigure
from Products.PloneTestCase import PloneTestCase as ptc
from Products.PloneTestCase.layer import PloneSite
ptc.setupPloneSite(
    extension_profiles=('stxnext.transform.avi2flv:default',)
)

import stxnext.transform.avi2flv

class TestCase(ptc.PloneTestCase):

    class layer(PloneSite):
        @classmethod
        def setUp(cls):
            fiveconfigure.debug_mode = True
            zcml.load_config('configure.zcml', stxnext.transform.avi2flv)
            fiveconfigure.debug_mode = False

        @classmethod
        def tearDown(cls):
            pass


def test_suite():
    return unittest.TestSuite([

        ## Unit tests
        doctestunit.DocFileSuite(
            'avi2flv.txt', package='stxnext.transform.avi2flv',
            setUp=testing.setUp, tearDown=testing.tearDown),

        ## Integration tests that use PloneTestCase
        ztc.ZopeDocFileSuite(
            'avi_to_flv.txt', package='stxnext.transform.avi2flv',
            test_class=TestCase),

        ## Functiona tests
        ztc.FunctionalDocFileSuite(
            'browser.txt', package='stxnext.transform.avi2flv',
            test_class=TestCase),

        ])

if __name__ == '__main__':
    unittest.main(defaultTest='DocBookTestCase')
