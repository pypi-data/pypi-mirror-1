# -*- coding: utf-8 -*-

import os.path
import unittest

from zope.testing import doctest, module
from zope.app.testing import functional

ftesting_zcml = os.path.join(os.path.dirname(__file__), 'ftesting.zcml')
FunctionalLayer = functional.ZCMLLayer(
    ftesting_zcml, __name__, 'FunctionalLayer', allow_teardown=True
    )


def setUp(test):
    module.setUp(test, 'dolmen.app.breadcrumbs.ftests')

def tearDown(test):
    module.tearDown(test)

def test_suite():
    suite = unittest.TestSuite()
    readme = functional.FunctionalDocFileSuite(
        'README.txt', setUp=setUp, tearDown=tearDown,
        )
    readme.layer = FunctionalLayer
    suite.addTest(readme)
    return suite
