import os.path
from zope.testing import doctest
from zope.app.testing import functional

ftesting_zcml = os.path.join(os.path.dirname(__file__), 'ftesting.zcml')
FunctionalLayer = functional.ZCMLLayer(ftesting_zcml, __name__,
                                       'FunctionalLayer')

xhtml = """<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN"
    "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
    <html xmlns="http://www.w3.org/1999/xhtml">
    <head>
    <title>html title</title>
    <meta http-equiv="content-type" content="text/html; charset=iso-8859-1" />
    </head>
    <body>
        <h2>long title</h2>
        <a href="./relative/link">link</a>
    </body>
</html>"""


def FunctionalDocTestSuite(module=None, **kw):
    module = doctest._normalize_module(module)
    suite = functional.FunctionalDocTestSuite(module, **kw)
    suite.layer = FunctionalLayer
    return suite

def FunctionalDocFileSuite(path, **kw):
    suite = functional.FunctionalDocFileSuite(path, **kw)
    suite.layer = FunctionalLayer
    return suite

class FunctionalTestCase(functional.FunctionalTestCase):
    layer = FunctionalLayer
