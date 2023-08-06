import os.path
import unittest
import doctest
from zope.app.testing import functional

ftesting_zcml = os.path.join(os.path.dirname(__file__), 'ftesting.zcml')
FunctionalLayer = functional.ZCMLLayer(
    ftesting_zcml, __name__, 'FunctionalLayer', allow_teardown=True
    )

def test_suite():
    suite = unittest.TestSuite()
    readme = functional.FunctionalDocFileSuite(
        'README.txt',
        globs={'__name__':'dolmen.app.content.tests'},
        )
    readme.layer = FunctionalLayer
    suite.addTest(readme)
    return suite
