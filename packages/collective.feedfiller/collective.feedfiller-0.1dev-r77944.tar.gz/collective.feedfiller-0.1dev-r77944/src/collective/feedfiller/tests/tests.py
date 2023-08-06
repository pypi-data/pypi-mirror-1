import unittest

from zope.testing import doctest
from zope.component import testing
from Testing import ZopeTestCase as ztc

from Products.Five import zcml
from Products.Five import fiveconfigure
from Products.PloneTestCase import PloneTestCase as ptc
from Products.PloneTestCase.layer import PloneSite
from Products.feedfeeder.tests.MainTestCase import MainTestCase as FFTestCase
ptc.setupPloneSite()

import collective.feedfiller

optionflags = (doctest.ELLIPSIS |
               doctest.NORMALIZE_WHITESPACE)
#                |
#               doctest.REPORT_ONLY_FIRST_FAILURE)

zope_doc_tests = "../adapters.py  ../flayregistry.py ../flay.py".split()
#We don'tneed the ../ for plone doc tests
plone_doc_tests = "doc/integration.txt README.txt  handlers.txt".split()

class TestCase(ptc.PloneTestCase):
    class layer(PloneSite):
        @classmethod
        def setUp(cls):
            fiveconfigure.debug_mode = True
            zcml.load_config('configure.zcml',
                             collective.feedfiller)
            fiveconfigure.debug_mode = False

        @classmethod
        def tearDown(cls):
            pass


def test_suite():
    return unittest.TestSuite(
             [
                 doctest.DocFileSuite(
                     dtfile,
                     setUp=testing.setUp, tearDown=testing.tearDown,
                     optionflags=optionflags
                 )
     
                for dtfile in zope_doc_tests
             ] 
             +
             [
             
                 ztc.ZopeDocFileSuite(
                     dtfile, package='collective.feedfiller',
                     test_class=TestCase)
             
                 for dtfile in plone_doc_tests
                 
             ]
    
     )

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
