"""Tests for ``collective.facetednavigation`` installation and
uninstallation.

$Id: test_installation.py 73039 2008-10-05 22:04:52Z dbaty $
"""

from Products.CMFCore.utils import getToolByName

from collective.facetednavigation.tool import CATALOG_ID
from collective.facetednavigation.tool import CONF_TOOL_ID

from collective.facetednavigation.tests.base import FacetedNavigationTestCase


class TestInstallation(FacetedNavigationTestCase):
    """Make sure that the product is properly installed."""

    def testUserInterfaceIsHere(self):
        ## This should not raise any error.
        self.portal.restrictedTraverse('faceted-navigation')


    def testToolIsHere(self):
        tool = getToolByName(self.portal, CONF_TOOL_ID, None)
        self.failUnless(tool is not None)


    def testCatalogIsHere(self):
        catalog = getToolByName(self.portal, CATALOG_ID, None)
        self.failUnless(catalog is not None)


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestInstallation))
    return suite
