import unittest
from doctest import DocFileSuite, DocTestSuite

import zope.component.testing

from vice.outbound.interfaces import IFeed

def setUp(test):
    #zope.component.testing.setUp(test)
    #zope.component.provideAdapter(RecipeReadFile)
    pass

def test_suite():
    return unittest.TestSuite((
# removed, as adapters have been moved to vice.zope2.outbound
# All docfile tests were removed, as they now run from test.py
#        DocTestSuite('vice.outbound.adapters',
#                     setUp=zope.component.testing.setUp,
#                     tearDown=zope.component.testing.tearDown),
        ))

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
