"""Tests for ``collective.facetednavigation.browser.utils`` module.

$Id: test_browser_utils.py 69976 2008-08-14 22:44:45Z dbaty $
"""

from collective.facetednavigation.tests.base import FacetedNavigationTestCase

from Products.CMFPlone import Batch

from collective.facetednavigation.browser import utils


class TestBrowserUtils(FacetedNavigationTestCase):
    """Make sure that ``browser.utils`` works."""

    def test_renderTemplateMacro(self):
        ## FIXME: find a macro that needs a little less set up...
        class FakeRequest:
            __allow_access_to_unprotected_subobjects__ = True
            form = {}
        rendered = utils.renderTemplateMacro(self.portal,
                                             'batch_macros',
                                             'navigation',
                                             {'batch': Batch(range(1, 10), 5),
                                              'template_id': 'test',
                                              'here': self.portal,
                                              'request': FakeRequest()})
        self.failUnless('<!-- Link to first -->' in rendered)


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestBrowserUtils))
    return suite
