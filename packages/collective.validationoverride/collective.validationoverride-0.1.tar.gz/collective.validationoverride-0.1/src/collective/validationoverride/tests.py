import unittest
from zope.testing import doctest

from Testing import ZopeTestCase
from Products.PloneTestCase import ptc

from collective.testcaselayer import ptc as tcl_ptc

optionflags = (doctest.NORMALIZE_WHITESPACE|
               doctest.ELLIPSIS|
               doctest.REPORT_NDIFF)

def test_suite():
    suite = ZopeTestCase.FunctionalDocFileSuite(
        'README.txt',
        optionflags=optionflags,
        test_class=ptc.FunctionalTestCase)
    suite.layer = tcl_ptc.ptc_layer
    return unittest.TestSuite([suite])

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
