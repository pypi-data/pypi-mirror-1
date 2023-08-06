""" Test case for archetypes.rolefield.
"""

import unittest
from Testing import ZopeTestCase
from zope.testing import doctest
from Testing.ZopeTestCase import ZopeDocFileSuite
from Testing.ZopeTestCase import FunctionalDocFileSuite
from Products.PloneTestCase import PloneTestCase
from Products.CMFPlone.utils import safe_hasattr, base_hasattr
from zope.component import getUtility, getMultiAdapter
from Products.PloneTestCase.layer import onsetup
from Products.Five import zcml

import zope.component.testing

__docformat__ = "reStructuredText"

@onsetup
def setup_package():
    import archetypes.rolefield
    zcml.load_config('configure.zcml', archetypes.rolefield)
    ZopeTestCase.installPackage('archetypes.rolefield')

setup_package()

# Create plone site instance
PloneTestCase.setupPloneSite(extension_profiles=['archetypes.rolefield:demo'])

OPTIONFLAGS = (doctest.ELLIPSIS |
               doctest.NORMALIZE_WHITESPACE)



def test_suite():
    tests = ['rolefield.txt']

    suite = unittest.TestSuite()
    for test in tests:
        suite.addTest(
            FunctionalDocFileSuite(
                test,
                package="archetypes.rolefield.tests",
                optionflags=OPTIONFLAGS,
                test_class=PloneTestCase.FunctionalTestCase)
            )
    return suite


if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
