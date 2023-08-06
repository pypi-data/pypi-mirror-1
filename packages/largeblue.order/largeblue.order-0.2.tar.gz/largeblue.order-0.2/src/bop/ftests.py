import unittest

import zope
import os.path
from zope.testing import doctest, doctestunit, module
from zope.app.testing.functional import FunctionalDocFileSuite, ZCMLLayer
from zope.publisher.browser import TestRequest

import bop

BopLayer = ZCMLLayer(
    os.path.join(os.path.split(__file__)[0], 'ftesting.zcml'),
    __name__, 'BopLayer', allow_teardown=True)


def setUp(test):
    module.setUp(test, 'bop.readme_txt')

def tearDown(test):
    module.tearDown(test, 'bop.readme_txt')


def test_suite():
    suite = unittest.TestSuite()
    
    globs = {'zope':zope,
            'pprint': doctestunit.pprint,
            'TestRequest': TestRequest,
            'bop': bop}

    for file in ('html.txt', 'pdf.txt', 'rdf.txt', 'shortref.txt',
                 'soup.txt', 'unapi.txt', 'util.txt'):
        test = FunctionalDocFileSuite(file,
            package='bop',
            globs=globs,
            optionflags=doctest.NORMALIZE_WHITESPACE+doctest.ELLIPSIS,
            setUp=setUp,
            tearDown=tearDown)
        test.layer = BopLayer
        suite.addTest(test)

    return suite

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
