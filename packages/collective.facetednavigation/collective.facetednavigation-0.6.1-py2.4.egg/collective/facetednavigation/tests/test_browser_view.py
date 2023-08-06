"""Tests for main browser view of ``collective.facetednavigation``.

$Id: test_browser_view.py 69976 2008-08-14 22:44:45Z dbaty $
"""

from collective.facetednavigation.tests.base import FacetedNavigationTestCase

from Products.PythonScripts.PythonScript import PythonScript

from Products.CMFCore.utils import getToolByName

from collective.facetednavigation.tool import ID as TOOL_ID
from collective.facetednavigation.browser.facetednavigation import FacetedNavigation
from collective.facetednavigation.browser.facetednavigation import MAIN_SESSION_KEY


class TestBrowserView(FacetedNavigationTestCase):
    """Make sure that the main browser view correctly works."""

    def afterSetUp(self):
        """Called before each tests:

        - add a ``getTitleFirstWord`` Python script to the root of the
          portal (the same could probably be achieved with an adapter
          but, "frankly, my dear, I don't give a damn");

        - define additional index and metadata ``getTitleFirstWord``;

        - remove unneeded content;

        - add test content;

        - configure Faceted Navigation.
        """
        FacetedNavigationTestCase.afterSetUp(self)
        portal = self.portal

        ## Add Python script
        script = PythonScript('getTitleFirstWord')
        portal._setObject('getTitleFirstWord', script)
        script.write('return context.Title() and '\
                     'context.Title().split(' ')[0] or '\
                     '""')

        ## Add catalog index and metadata
        catalog = portal.portal_catalog
        catalog.addIndex('getTitleFirstWord', 'FieldIndex')
        catalog.addColumn('getTitleFirstWord')

        ## Remove unneeded content
        self.setRoles(['Manager'])
        portal.manage_delObjects(['front-page', 'events', 'news', 'Members'])

        ## Add test content, following this scheme:
        ##  1. News 01 (keyword1)
        ##  2. Document 02 (keyword2)
        ##  3. News 03 (keyword1, keyword2)
        ##  4. Document 04 (<no keyword>)
        ##  ...
        ##  37. News 37 (keyword1)
        ##  38. Document 38 (keyword2)
        ##  39. News 39 (keyword1, keyword2)
        ##  40. Document 40 (<no keyword>)
        for i in range(1, 41):
            portal_type = ['Document', 'News Item'][i % 2]
            item_id = ['document-%02d', 'news-%02d'][i % 2] % i
            title = ['Document %02d', 'News %02d'][i % 2] % i
            subject = [(),
                       ('keyword1', ),
                       ('keyword2', ),
                       ('keyword1', 'keyword2')][i % 4]
            portal.invokeFactory(portal_type, item_id)
            item = portal[item_id]
            item.setTitle(title)
            item.setSubject(subject)
            item.reindexObject()

        ## Make sure that everything is as intended.
        catalog = portal.portal_catalog
        self.failUnlessEqual(len(catalog()), 40)
        self.failUnlessEqual(len(catalog(Subject='keyword1')), 20)
        self.failUnlessEqual(len(catalog(Subject='keyword2')), 20)
        self.failUnlessEqual(len(catalog(Subject=('keyword1', 'keyword2'))), 30)
        self.failUnlessEqual(len(catalog(Subject={'query': ('keyword1',
                                                            'keyword2'),
                                                  'operator': 'and'})),
                             10)
        self.failUnlessEqual(len(catalog(meta_type='ATDocument')), 20)
        self.failUnlessEqual(len(catalog(meta_type='ATNewsItem')), 20)
        self.failUnlessEqual(len(catalog(getTitleFirstWord='Document')), 20)
        self.failUnlessEqual(len(catalog(getTitleFirstWord='News')), 20)

        ## Configure Faceted Navigation
        config = getToolByName(portal, TOOL_ID)
        left_facets = ('Subject', )
        right_facets = ('getTitleFirstWord;First word of title',
                        'getRawRelatedItems;Related items;Title')
        config.manage_changeProperties(left_facets=left_facets,
                                       right_facets=right_facets)

        self.setRoles([])


    def test_getLabelOf(self):
        view = FacetedNavigation(self.portal, self.app.REQUEST)
        brain = self.portal.portal_catalog()[0]
        self.failUnlessEqual(view.getLabelOf(brain.UID, 'Title'),
                             brain.Title)
        self.failUnlessEqual(view.getLabelOf('012345', 'Title'),
                             '<unknown (012345)>')


    def test_getMatchingItems(self):

        def getMatchingItems(criteria):
            request = self._getNewRequest({MAIN_SESSION_KEY: criteria})
            view = FacetedNavigation(self.portal, request)
            return view.getMatchingItems()

        ## Test basic behaviour
        for criteria, expected in \
            (({}, 40),
             ({'getTitleFirstWord': 'Document'}, 20),
             ({'Subject': 'keyword1'}, 20),
             ({'getTitleFirstWord': 'News',
               'Subject': 'keyword1'}, 20),
             ({'getTitleFirstWord': 'Document',
               'Subject': 'keyword1'}, 0),
             ({'getTitleFirstWord': 'News',
               'Subject': ('keyword1', 'keyword2')}, 10)):
            self.failUnlessEqual(getMatchingItems(criteria).total_length,
                                 expected)

        tool = getToolByName(self.portal, TOOL_ID)

        ## Restrict meta_types to 'ATNewsItem' only
        tool.manage_changeProperties(meta_types=['ATNewsItem'])
        self.failUnlessEqual(getMatchingItems({}).total_length, 20)

        ## Test 'sort_on' and 'sort_order' properties
        tool.manage_changeProperties(sort_on='getId')
        items = getMatchingItems({})
        self.failUnlessEqual(items[0].getId, 'news-01')
        self.failUnlessEqual(items[-1].getId, 'news-39')

        tool.manage_changeProperties(sort_order='reverse')
        items = getMatchingItems({})
        self.failUnlessEqual(items[0].getId, 'news-39')
        self.failUnlessEqual(items[-1].getId, 'news-01')

        ## Test with an index that do not support sorting, for
        ## instance 'Title'
        tool.manage_changeProperties(sort_on='Title',
                                     sort_order='')
        items = getMatchingItems({})
        self.failUnlessEqual(items[0].Title, 'News 01')
        self.failUnlessEqual(items[-1].Title, 'News 39')

        tool.manage_changeProperties(sort_order='reverse')
        items = getMatchingItems({})
        self.failUnlessEqual(items[0].Title, 'News 39')
        self.failUnlessEqual(items[-1].Title, 'News 01')


    def test_getResults(self):

        def getResults(criteria):
            request = self._getNewRequest({MAIN_SESSION_KEY: criteria})
            view = FacetedNavigation(self.portal, request)
            return view.getResults()

        ## Test basic behaviour
        results = getResults({})
        self.failUnlessEqual(results,
                             {'getTitleFirstWord': [{'value': 'Document',
                                                     'label': 'Document',
                                                     'n_results': 20},
                                                    {'value': 'News',
                                                     'label': 'News',
                                                     'n_results': 20}],
                              'Subject': [{'value': 'keyword1',
                                           'label': 'keyword1',
                                           'n_results': 20},
                                          {'value': 'keyword2',
                                           'label': 'keyword2',
                                           'n_results': 20}],
                              'getRawRelatedItems': [],
                              })

        results = getResults({'Subject': 'keyword2'})
        self.failUnlessEqual(results,
                             {'getTitleFirstWord': [{'value': 'Document',
                                                     'label': 'Document',
                                                     'n_results': 10},
                                                    {'value': 'News',
                                                     'label': 'News',
                                                     'n_results': 10}
                                                    ],
                              'Subject': [{'value': 'keyword2',
                                           'label': 'keyword2',
                                           'n_results': 20},
                                          {'value': 'keyword1',
                                           'label': 'keyword1',
                                           'n_results': 10}],
                              'getRawRelatedItems': [],
                              })

        results = getResults({'Subject': ('keyword1', 'keyword2')})
        self.failUnlessEqual(results,
                             {'getTitleFirstWord': [{'value': 'News',
                                                     'label': 'News',
                                                     'n_results': 10}],
                              'Subject': [{'value': 'keyword1',
                                           'label': 'keyword1',
                                           'n_results': 10},
                                          {'value': 'keyword2',
                                           'label': 'keyword2',
                                           'n_results': 10}],
                              'getRawRelatedItems': [],
                              })

        ## Test a facet that uses UID
        news_01_uid = self.portal['news-01'].UID()
        document_02_uid = self.portal['document-02'].UID()
        for i in range(1, 9):
            item_id = ['document-%02d', 'news-%02d'][i % 2] % i
            related_item_uid = [news_01_uid, document_02_uid][i % 2]
            item = self.portal[item_id]
            item.setRelatedItems([related_item_uid])
            item.reindexObject()

        ## This will not work because there is no 'getRawRelatedItems'
        ## metadata (see also following test).
        results = getResults({})
        self.failUnlessEqual(results,
                             {'getTitleFirstWord': [{'value': 'Document',
                                                     'label': 'Document',
                                                     'n_results': 20},
                                                    {'value': 'News',
                                                     'label': 'News',
                                                     'n_results': 20}],
                              'Subject': [{'value': 'keyword1',
                                           'label': 'keyword1',
                                           'n_results': 20},
                                          {'value': 'keyword2',
                                           'label': 'keyword2',
                                           'n_results': 20}],
                              'getRawRelatedItems': [],
                              })

        ## Though if we add the metadata and reindex everything, we
        ## will get what we expect.
        catalog = getToolByName(self.portal, 'portal_catalog')
        catalog.addColumn('getRawRelatedItems')
        catalog.refreshCatalog(clear=True)
        results = getResults({})
        self.failUnlessEqual(results,
                             {'getTitleFirstWord': [{'value': 'Document',
                                                     'label': 'Document',
                                                     'n_results': 20},
                                                    {'value': 'News',
                                                     'label': 'News',
                                                     'n_results': 20}],
                              'Subject': [{'value': 'keyword1',
                                           'label': 'keyword1',
                                           'n_results': 20},
                                          {'value': 'keyword2',
                                           'label': 'keyword2',
                                           'n_results': 20}],
                              'getRawRelatedItems': [{'value': document_02_uid,
                                                      'label': 'Document 02',
                                                      'n_results': 4},
                                                     {'value': news_01_uid,
                                                      'label': 'News 01',
                                                      'n_results': 4}],
                              })

        ## Test 'Missing.Value' handling, when the index has no value
        ## for a particular object. In this case, we will use the
        ## 'end' index.
        tool = getToolByName(self.portal, TOOL_ID)
        tool.manage_changeProperties(left_facets=('Subject',
                                                  'end'))
        results = getResults({})
        self.failUnlessEqual(results,
                             {'getTitleFirstWord': [{'value': 'Document',
                                                     'label': 'Document',
                                                     'n_results': 20},
                                                    {'value': 'News',
                                                     'label': 'News',
                                                     'n_results': 20}],
                              'Subject': [{'value': 'keyword1',
                                           'label': 'keyword1',
                                           'n_results': 20},
                                          {'value': 'keyword2',
                                           'label': 'keyword2',
                                           'n_results': 20}],
                              'end': [],
                              'getRawRelatedItems': [{'value': document_02_uid,
                                                      'label': 'Document 02',
                                                      'n_results': 4},
                                                     {'value': news_01_uid,
                                                      'label': 'News 01',
                                                      'n_results': 4}],
                              })

        ## Test that if we remove a particular index and its metadata,
        ## the corresponding facet is ignored.
        catalog.delIndex('getTitleFirstWord')
        catalog.delColumn('getTitleFirstWord')
        catalog.refreshCatalog(clear=True)
        tool.manage_changeProperties(left_facets=('getTitleFirstWord', ),
                                     right_facets=())
        results = getResults({})
        self.failUnlessEqual(results, {'getTitleFirstWord': []})


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestBrowserView))
    return suite
