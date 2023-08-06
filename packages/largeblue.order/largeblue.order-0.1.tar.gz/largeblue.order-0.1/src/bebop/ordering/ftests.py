import unittest, doctest
import tempfile, os, os.path

import zope.component
from zope.testing import module
from zope.app.testing.functional import FunctionalDocFileSuite, ZCMLLayer

BebopOrderingLayer = ZCMLLayer(
    os.path.join(os.path.split(__file__)[0], 'ftesting.zcml'),
    __name__, 'BebopOrderingLayer', allow_teardown=True)

def setUp(test):
    module.setUp(test, 'bebop.ordering.readme_txt')

def tearDown(test):
    module.tearDown(test, 'bebop.ordering.readme_txt')

def test_suite():
    options = doctest.NORMALIZE_WHITESPACE+doctest.ELLIPSIS
    suite = unittest.TestSuite()
    
    test = FunctionalDocFileSuite(
        'README.txt',
        package='bebop.ordering',
        optionflags=options,
        setUp=setUp,
        tearDown=tearDown)
        
    test.layer = BebopOrderingLayer
    suite.addTest(test)
    return suite

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
