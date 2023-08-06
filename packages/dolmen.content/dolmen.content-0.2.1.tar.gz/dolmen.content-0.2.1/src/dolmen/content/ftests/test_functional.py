import os.path
import unittest
from pkg_resources import resource_listdir
from zope.testing import doctest
from zope.app.testing import functional

ftesting_zcml = os.path.join(os.path.dirname(__file__), 'ftesting.zcml')
FunctionalLayer = functional.ZCMLLayer(
    ftesting_zcml, __name__, 'FunctionalLayer',  allow_teardown=True)


def suiteFromPackage(name):
    files = resource_listdir(__name__, name)
    suite = unittest.TestSuite()
    for filename in files:
        if not filename.endswith('.py'):
            continue
        if filename == '__init__.py':
            continue

        dottedname = 'dolmen.content.ftests.%s.%s' % (name, filename[:-3])
        test = doctest.DocTestSuite(
            dottedname,
            optionflags=(doctest.ELLIPSIS+
                         doctest.NORMALIZE_WHITESPACE+
                         doctest.REPORT_NDIFF)
            )
        test.layer = FunctionalLayer

        suite.addTest(test)
    return suite


def test_suite():
    suite = unittest.TestSuite()
    
    readme = functional.FunctionalDocFileSuite(
        '../README.txt',
        globs={"__name__": 'dolmen.content'},
        optionflags=(doctest.ELLIPSIS + doctest.NORMALIZE_WHITESPACE),
        )
    readme.layer = FunctionalLayer
    suite.addTest(readme)

    for name in ['content']:
        suite.addTest(suiteFromPackage(name))
    return suite
