"""Tests ``collective.facetednavigation`` tool.

$Id: test_tool.py 73039 2008-10-05 22:04:52Z dbaty $
"""

from Products.CMFCore.utils import getToolByName

from collective.facetednavigation.tests.base import FacetedNavigationTestCase

from collective.facetednavigation.tool import CONF_TOOL_ID


class TestTool(FacetedNavigationTestCase):
    """Make sure that the tool behaves correctly."""

    def test_getFacets(self):
        tool = getToolByName(self.portal, CONF_TOOL_ID)
        left_facets = ('facet1;',
                       'facet2;Facet 2',
                       'facet3;Facet 3;foo',
                       'facet4;Facet 4;;calendar')
        right_facets = ('facet5;Facet 5;foo;calendar',
                        'facet6;;foo;calendar')
        tool.manage_changeProperties(left_facets=left_facets,
                                     right_facets=right_facets)

        left = [{'id': 'facet1',
                 'label': 'facet1',
                 'uid_attribute': None,
                 'widget': 'checkboxes'},
                {'id': 'facet2',
                 'label': 'Facet 2',
                 'uid_attribute': None,
                 'widget': 'checkboxes'},
                {'id': 'facet3',
                 'label': 'Facet 3',
                 'uid_attribute': 'foo',
                 'widget': 'checkboxes'},
                {'id': 'facet4',
                 'label': 'Facet 4',
                 'uid_attribute': None,
                 'widget': 'calendar'},]
        right = [{'id': 'facet5',
                  'label': 'Facet 5',
                  'uid_attribute': 'foo',
                  'widget': 'calendar'},
                 {'id': 'facet6',
                  'label': 'facet6',
                  'uid_attribute': 'foo',
                  'widget': 'calendar'},]
        self.failUnlessEqual(tool.getLeftFacets(), left)
        self.failUnlessEqual(tool.getRightFacets(), right)
        self.failUnlessEqual(tool.getAllFacets(), left + right)


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestTool))
    return suite
