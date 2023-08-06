"""Vice functional doctests.  This module collects all *.txt
files in the tests directory and runs them. (stolen from Plone via PloneBoard)
"""

import os, sys

import glob
import doctest
import unittest
try : # zope2
    from Globals import package_home
except ImportError: # zope3
    def package_home(gdict):
        filename = gdict["__file__"]
        return os.path.dirname(filename)
try: # zope2
    from Testing.ZopeTestCase import FunctionalDocFileSuite as Suite, \
                                     FunctionalTestCase
except ImportError: # zope3
    from zope.app.testing.functional import FunctionalDocFileSuite as Suite, \
                                            FunctionalTestCase
from vice.outbound.config import GLOBALS

OPTIONFLAGS = (doctest.REPORT_ONLY_FIRST_FAILURE |
               doctest.ELLIPSIS |
               doctest.NORMALIZE_WHITESPACE)

def list_doctests(prefix=''):
    home = package_home(GLOBALS)
    doctests = [os.path.sep.join(['tests',os.path.basename(filename)]) 
                for filename in 
                glob.glob(os.path.sep.join([home, 'tests', prefix + '*.txt']))]
    doctests.extend([os.path.basename(filename) for filename in
                     glob.glob(os.path.sep.join([home, prefix + '*.py']))])
    doctests.extend(['%s/%s' % ('adapters', os.path.basename(filename)) for filename in
                     glob.glob(os.path.sep.join([home, 'adapters', '*.py']))])
    doctests.extend(['%s/%s' % ('browser', os.path.basename(filename)) for filename in
                     glob.glob(os.path.sep.join([home, 'browser', '*.py']))])
    doctests.extend(['%s/%s' % ('feedformats', os.path.basename(filename)) for filename in
                    glob.glob(os.path.sep.join([home, 'feedformats', '*.py']))])
    return doctests


def test_suite():
    return unittest.TestSuite(
        [Suite(filename,
               optionflags=OPTIONFLAGS,
               package='vice.outbound',)
# commented out for zope3 - how does this affect zope2?
#               test_class=FunctionalTestCase)
         for filename in list_doctests()]
        )
