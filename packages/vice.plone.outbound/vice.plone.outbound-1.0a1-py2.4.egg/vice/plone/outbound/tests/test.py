"""Vice functional doctests.  This module collects all *.txt
files in the tests directory and runs them. (stolen from Plone via PloneBoard)
"""

import os, sys

import glob
import doctest
import unittest
from Globals import package_home
from Products.PloneTestCase import PloneTestCase
from Products.PloneTestCase.layer import onsetup
from Testing.ZopeTestCase import FunctionalDocFileSuite as Suite

from vice.plone.outbound.config import GLOBALS

from vice.plone.outbound.tests.vicetestcase \
    import ViceFunctionalTestCase

@onsetup
def setup_vice():
    try:
        from Products.Five import zcml
        from Products.Five import fiveconfigure
        fiveconfigure.debug_mode = True
        import five.intid
        zcml.load_config('configure.zcml', five.intid)
        import vice.outbound
        zcml.load_config('configure.zcml', vice.outbound)
        import vice.plone.outbound
        zcml.load_config('configure.zcml', vice.plone.outbound)
        fiveconfigure.debug_mode = False
    except ImportError:
        pass # not zope 2

setup_vice()

OPTIONFLAGS = (doctest.REPORT_ONLY_FIRST_FAILURE |
               doctest.ELLIPSIS |
               doctest.NORMALIZE_WHITESPACE)

def list_doctests(prefix=''):
    home = package_home(GLOBALS)
    return [filename for filename in
            glob.glob(os.path.sep.join([home, 'tests', prefix + '*.txt']))]

def test_suite():
    return unittest.TestSuite(
        [Suite(os.path.basename(filename),
               optionflags=OPTIONFLAGS,
               package='vice.plone.outbound.tests',
               test_class=ViceFunctionalTestCase)
         for filename in list_doctests()]
        )
