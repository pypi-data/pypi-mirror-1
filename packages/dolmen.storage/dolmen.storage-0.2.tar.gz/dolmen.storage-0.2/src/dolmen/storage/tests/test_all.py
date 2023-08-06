# -*- coding: utf-8 -*-

import os.path
import unittest
import pkg_resources

from zope.testing import doctest
from zope.app.testing import functional

ftesting_zcml = os.path.join(os.path.dirname(__file__), 'ftesting.zcml')
FunctionalLayer = functional.ZCMLLayer(
    ftesting_zcml, __name__, 'FunctionalLayer', allow_teardown=True)


def suiteFromPackage(name):
    files = pkg_resources.resource_listdir(__name__, name)
    suite = unittest.TestSuite()
    for filename in files:
        if not filename.endswith('.py'):
            continue
        if filename.endswith('_fixture.py'):
            continue
        if filename == '__init__.py':
            continue

        dottedname = 'dolmen.storage.tests.%s.%s' % (name, filename[:-3])
        test = doctest.DocTestSuite(
            dottedname,
            optionflags=doctest.ELLIPSIS+doctest.NORMALIZE_WHITESPACE)
        suite.addTest(test)
    return suite


def test_suite():
    suite = unittest.TestSuite()

    readme = functional.FunctionalDocFileSuite(
        '../README.txt',
        optionflags=(doctest.ELLIPSIS + doctest.NORMALIZE_WHITESPACE),
        )
    readme.layer = FunctionalLayer
    suite.addTest(readme)
    
    for name in ['container', 'annotations']:
        suite.addTest(suiteFromPackage(name))
    
    return suite


if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
