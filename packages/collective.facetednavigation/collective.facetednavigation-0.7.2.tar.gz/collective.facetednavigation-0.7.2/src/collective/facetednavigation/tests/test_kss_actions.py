"""Tests for KSS actions of ``collective.facetednavigation``.

$Id: test_kss_actions.py 69976 2008-08-14 22:44:45Z dbaty $
"""

from collective.facetednavigation.tests.base import FacetedNavigationTestCase

from collective.facetednavigation.browser.facetednavigation import FacetedNavigation
from collective.facetednavigation.browser.facetednavigation import KSSFacetedActions
from collective.facetednavigation.browser.facetednavigation import MAIN_SESSION_KEY


## FIXME: For now, only the logic is tested. The user interface is not
## tested.
class TestKSSActions(FacetedNavigationTestCase):
    """Make sure that KSS actions correctly work."""


    def test_selectValue(self):
        request = self._getNewRequest({MAIN_SESSION_KEY: {}})
        kss = KSSFacetedActions(self.portal, request)
        browser = FacetedNavigation(self.portal, request)

        kss.selectValue('facet1-value1')
        self.failUnless(browser.valueIsSelected('facet1', 'value1'))
        self.failUnless(not browser.valueIsSelected('facet1', 'value2'))

        kss.selectValue('facet1-value1')
        self.failUnless(not browser.valueIsSelected('facet1', 'value1'))

        kss.selectValue('facet1-value1')
        self.failUnless(browser.valueIsSelected('facet1', 'value1'))

        kss.selectValue('facet1-value2')
        self.failUnless(browser.valueIsSelected('facet1', 'value1'))
        self.failUnless(browser.valueIsSelected('facet1', 'value2'))

        kss.selectValue('facet1-value1')
        self.failUnless(not browser.valueIsSelected('facet1', 'value1'))
        self.failUnless(browser.valueIsSelected('facet1', 'value2'))

        kss.selectValue('facet2-value1')
        self.failUnless(not browser.valueIsSelected('facet1', 'value1'))
        self.failUnless(browser.valueIsSelected('facet1', 'value2'))
        self.failUnless(browser.valueIsSelected('facet2', 'value1'))


    def test_resetSelection(self):
        request = self._getNewRequest({MAIN_SESSION_KEY: {}})
        kss = KSSFacetedActions(self.portal, request)
        browser = FacetedNavigation(self.portal, request)

        kss.selectValue('facet1-value1')
        kss.selectValue('facet1-value2')
        kss.selectValue('facet2-value1')
        self.failUnless(browser.valueIsSelected('facet1', 'value1'))
        self.failUnless(browser.valueIsSelected('facet1', 'value2'))
        self.failUnless(browser.valueIsSelected('facet2', 'value1'))

        kss.resetSelection()
        self.failUnlessEqual(browser.request.SESSION,
                             {MAIN_SESSION_KEY: {}})


    def test_showOrHideFacetBlock(self):
        request = self._getNewRequest({MAIN_SESSION_KEY: {}})
        kss = KSSFacetedActions(self.portal, request)
        browser = FacetedNavigation(self.portal, request)

        kss.showOrHideFacetBlock('facet1')
        self.failUnless(not browser.showFacet('facet1'))
        kss.showOrHideFacetBlock('facet1')
        self.failUnless(browser.showFacet('facet1'))
        kss.showOrHideFacetBlock('facet2')
        self.failUnless(browser.showFacet('facet1'))
        self.failUnless(not browser.showFacet('facet2'))


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestKSSActions))
    return suite
