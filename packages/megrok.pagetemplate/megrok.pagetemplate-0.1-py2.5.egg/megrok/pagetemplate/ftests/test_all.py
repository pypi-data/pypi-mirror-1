# -*- coding: utf-8 -*-

import re
import os.path
import unittest

from pkg_resources import resource_listdir
from zope.testing import doctest, module
from zope.app.testing import functional

ftesting_zcml = os.path.join(os.path.dirname(__file__), 'ftesting.zcml')
FunctionalLayer = functional.ZCMLLayer(
    ftesting_zcml, __name__, 'FunctionalLayer', allow_teardown=True
    )

def setUp(test):
    module.setUp(test, 'megrok.pagetemplate.ftests')

def tearDown(test):
    module.tearDown(test)

def FsetUp(test):
    functional.FunctionalTestSetup().setUp()

def FtearDown(test):
    functional.FunctionalTestSetup().tearDown()


def suiteFromPackage(name):
    files = resource_listdir(__name__, name)
    suite = unittest.TestSuite()
    for filename in files:
        if not filename.endswith('.py'):
            continue
        if filename == '__init__.py':
            continue

        dottedname = 'megrok.pagetemplate.ftests.%s.%s' % (name, filename[:-3])
        test = doctest.DocTestSuite(
            dottedname, setUp=FsetUp, tearDown=FtearDown,
            optionflags=doctest.NORMALIZE_WHITESPACE + doctest.ELLIPSIS
                         
            )
        test.layer = FunctionalLayer

        suite.addTest(test)
    return suite


def test_suite():
    suite = unittest.TestSuite()
    for name in ['usecases']:
        suite.addTest(suiteFromPackage(name))
        
    readme = functional.FunctionalDocFileSuite(
            '../README.txt', setUp=setUp, tearDown=tearDown,
            optionflags=(doctest.ELLIPSIS+
                         doctest.NORMALIZE_WHITESPACE)
            )
    readme.layer = FunctionalLayer
    suite.addTest(readme)
    return suite
