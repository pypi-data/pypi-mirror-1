# -*- coding: utf-8 -*-

import unittest
import dolmen.app.content
from zope.component.testlayer import ZCMLFileLayer
from zope.testing import doctest


class DolmenAppContentLayer(ZCMLFileLayer):
    pass


def test_suite():
    suite = unittest.TestSuite()
    readme = doctest.DocFileSuite(
        'README.txt',
        optionflags=(doctest.NORMALIZE_WHITESPACE | doctest.ELLIPSIS))
    readme.layer = ZCMLFileLayer(dolmen.app.content)
    suite.addTest(readme)
    return suite
