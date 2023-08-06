"""Tests for ``collective.facetednavigation`` installation and
uninstallation.

$Id: test_installation.py 69976 2008-08-14 22:44:45Z dbaty $
"""

from Products.CMFCore.utils import getToolByName

from collective.facetednavigation.tests.base import FacetedNavigationTestCase


class TestInstallation(FacetedNavigationTestCase):
    """Make sure that the product is properly installed."""

    def testUserInterfaceIsHere(self):
        ## This should not raise any error.
        self.portal.restrictedTraverse('faceted-navigation')



def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestInstallation))
    return suite
