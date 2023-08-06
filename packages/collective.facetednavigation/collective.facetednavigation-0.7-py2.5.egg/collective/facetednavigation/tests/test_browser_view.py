"""Tests for main browser view of ``collective.facetednavigation``.

$Id: test_browser_view.py 73039 2008-10-05 22:04:52Z dbaty $
"""

from collective.facetednavigation.tests.base import FacetedNavigationTestCase

from Products.ZCTextIndex.ZCTextIndex import PLexicon
from Products.PythonScripts.PythonScript import PythonScript

from Products.CMFCore.utils import getToolByName

from collective.facetednavigation.tool import CATALOG_ID
from collective.facetednavigation.tool import CONF_TOOL_ID
from collective.facetednavigation.browser.facetednavigation import MAIN_SESSION_KEY
from collective.facetednavigation.browser.facetednavigation import FacetedNavigation


def _addZCTextIndex(catalog):
        class _Extra: pass
        catalog._setObject('foo_plexicon', PLexicon('foo_plexicon'))
        extra = _Extra()
        extra.lexicon_id = 'foo_plexicon'
        extra.index_type = 'Okapi BM25 Rank'
        catalog.addIndex('Title', 'ZCTextIndex', extra)


class TestBrowserView(FacetedNavigationTestCase):
    """Make sure that the main browser view correctly works."""

    def afterSetUp(self):
        """Called before each tests:

        - add a ``getTitleFirstWord`` Python script to the root of the
          portal (the same could probably be achieved with an adapter
          but, *frankly, my dear, I don't give a damn*);

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

        ## Add catalog index and metadata and register our catalog for
        ## the content types we want to deal with.
        catalog = getToolByName(portal, CATALOG_ID)
        catalog.addIndex('getTitleFirstWord', 'FieldIndex')
        catalog.addColumn('getTitleFirstWord')
        catalog.addIndex('Subject', 'KeywordIndex')
        catalog.addColumn('Subject')
        catalog.addIndex('meta_type', 'FieldIndex')
        catalog.addColumn('meta_type')
        atool = getToolByName(self.portal, 'archetype_tool')
        for portal_type in ('Document', 'News Item'):
            atool.setCatalogsByType(portal_type, [CATALOG_ID])

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
        ftool = getToolByName(portal, CONF_TOOL_ID)
        left_facets = ('Subject', )
        right_facets = ('getTitleFirstWord', )
        ftool.manage_changeProperties(left_facets=left_facets,
                                       right_facets=right_facets)


    def test_getLabelOf(self):
        catalog = getToolByName(self.portal, CATALOG_ID)
        catalog.addIndex('UID', 'FieldIndex')
        catalog.addColumn('UID')
        catalog.addIndex('Title', 'FieldIndex')
        catalog.refreshCatalog(clear=True)

        view = FacetedNavigation(self.portal, self._getNewRequest())
        brain = catalog()[0]
        self.failUnlessEqual(view.getLabelOf(brain.UID, 'Title'),
                             brain.Title)
        self.failUnlessEqual(view.getLabelOf('012345', 'Title'),
                             '<unknown (012345)>')


    def _getMatchingItemsFunc(self):
        """Return ``FacetedNavigation.getMatchingItems`` of a new
        view.
        """
        def getMatchingItems(criteria):
            request = self._getNewRequest({MAIN_SESSION_KEY: criteria})
            view = FacetedNavigation(self.portal, request)
            return view.getMatchingItems()
        return getMatchingItems


    def test_getMatchingItems_basic(self):
        """Test basic behaviour of ``getMatchingItems()``."""
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
            items = self._getMatchingItemsFunc()(criteria)
            self.failUnlessEqual(items.total_length,
                                 expected)


    def test_getMatchingItems_restrict_meta_types(self):
        """Test meta_type restriction in ``getMatchingItems()``."""
        tool = getToolByName(self.portal, CONF_TOOL_ID)
        tool.manage_changeProperties(meta_types=['ATNewsItem'])
        items = self._getMatchingItemsFunc()({})
        self.failUnlessEqual(items.total_length, 20)


    def test_getMatchingItems_sort(self):
        """Test sort features in ``getMatchingItems()``."""
        catalog = getToolByName(self.portal, CATALOG_ID)
        catalog.addIndex('getId', 'FieldIndex')
        catalog.addColumn('getId')
        catalog.refreshCatalog(clear=True)

        tool = getToolByName(self.portal, CONF_TOOL_ID)
        getMatchingItems = self._getMatchingItemsFunc()

        tool.manage_changeProperties(sort_on='getId')
        items = getMatchingItems({})
        self.failUnlessEqual(items[0].getId, 'document-02')
        self.failUnlessEqual(items[-1].getId, 'news-39')

        tool.manage_changeProperties(sort_order='reverse')
        items = getMatchingItems({})
        self.failUnlessEqual(items[0].getId, 'news-39')
        self.failUnlessEqual(items[-1].getId, 'document-02')

        ## Test with an index that do not support sorting, for
        ## instance 'Title'
        _addZCTextIndex(catalog)
        catalog.refreshCatalog(clear=True)

        tool.manage_changeProperties(sort_on='Title', sort_order='')
        items = getMatchingItems({})
        self.failUnlessEqual(items[0].Title, 'Document 02')
        self.failUnlessEqual(items[-1].Title, 'News 39')

        tool.manage_changeProperties(sort_order='reverse')
        items = getMatchingItems({})
        self.failUnlessEqual(items[0].Title, 'News 39')
        self.failUnlessEqual(items[-1].Title, 'Document 02')


    def test_getMatchingItems_default_criteria(self):
        """Test ``default_criteria`` configuration."""
        tool = getToolByName(self.portal, CONF_TOOL_ID)
        getMatchingItems = self._getMatchingItemsFunc()

        self.failUnlessEqual(getMatchingItems({}).total_length, 40)
        self.failUnlessEqual(getMatchingItems({}).total_length, 40)

        catalog = getToolByName(self.portal, CATALOG_ID)
        catalog.addIndex('Type', 'FieldIndex')
        catalog.addColumn('Type')
        catalog.refreshCatalog(clear=True)

        tool.manage_changeProperties(default_criteria=['Type;Page'])
        self.failUnlessEqual(getMatchingItems({}).total_length, 20)


    def _getResultsFunc(self):
        """Return ``FacetedNavigation.getResults`` of a new view."""
        def getResults(criteria):
            request = self._getNewRequest({MAIN_SESSION_KEY: criteria})
            view = FacetedNavigation(self.portal, request)
            return view.getResults()
        return getResults


    def test_getResults_basic(self):
        getResults = self._getResultsFunc()

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
                                           'n_results': 20}]
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
                                           'n_results': 10}]
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
                                           'n_results': 10}]
                              })


    def test_getResults_missing_metadata(self):
        """Test the behaviour when a facet is associated to a metadata
        that is missing.
        """
        catalog = getToolByName(self.portal, CATALOG_ID)
        catalog.addColumn('getRawRelatedItems')
        ftool = getToolByName(self.portal, CONF_TOOL_ID)
        left_facets = list(ftool.getProperty('left_facets'))
        left_facets.append('getRawRelatedItems;Related items;Title')
        ftool.manage_changeProperties(left_facets=left_facets)

        ## Since there is no metadata for 'getRawRelatedItems', we get
        ## an empty result list for this facet
        results = self._getResultsFunc()({})
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


    def test_getResults_missing_index(self):
        """Test the behaviour when a facet is associated to an index
        that is missing.
        """
        catalog = getToolByName(self.portal, CATALOG_ID)
        catalog.delIndex('getTitleFirstWord')
        catalog.delColumn('getTitleFirstWord')
        catalog.refreshCatalog(clear=True)
        ftool = getToolByName(self.portal, CONF_TOOL_ID)
        ftool.manage_changeProperties(left_facets=('getTitleFirstWord', ),
                                      right_facets=())
        results = self._getResultsFunc()({})
        self.failUnlessEqual(results, {'getTitleFirstWord': []})


    def test_getResults_missing_value(self):
        """Test the behaviour when an index has no value
        (``Missing.Value``) for a facet metadata.
        """
        ## We use the 'end' index, which has no value for our
        ## documents and news items.
        tool = getToolByName(self.portal, CONF_TOOL_ID)
        tool.manage_changeProperties(left_facets=('Subject',
                                                  'end'))

        results = self._getResultsFunc()({})
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
                              })


    def test_getResults_uid(self):
        """Test with a facet that uses an UID."""
        catalog = getToolByName(self.portal, CATALOG_ID)
        catalog.addIndex('UID', 'FieldIndex')
        catalog.addColumn('getRawRelatedItems')
        catalog.refreshCatalog(clear=True)

        ftool = getToolByName(self.portal, CONF_TOOL_ID)
        left_facets = list(ftool.getProperty('left_facets'))
        left_facets.append('getRawRelatedItems;Related items;Title')
        ftool.manage_changeProperties(left_facets=left_facets)

        news_01_uid = self.portal['news-01'].UID()
        document_02_uid = self.portal['document-02'].UID()
        for i in range(1, 9):
            item_id = ['document-%02d', 'news-%02d'][i % 2] % i
            related_item_uid = [news_01_uid, document_02_uid][i % 2]
            item = self.portal[item_id]
            item.setRelatedItems([related_item_uid])
            item.reindexObject()

        results = self._getResultsFunc()({})
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


    def test_cache_policies_getResults_add_modify_remove(self):
        tool = getToolByName(self.portal, CONF_TOOL_ID)
        tool.manage_changeProperties(left_facets=[])
        tool.manage_changeProperties(right_facets=['getTitleFirstWord'])
        tool.manage_changeProperties(meta_types=['ATDocument'])

        expected = lambda n: {'getTitleFirstWord': \
                              [{'value': 'Document',
                                'label': 'Document',
                                'n_results': n}]}

        getResults = self._getResultsFunc()
        for policy in tool._getAvailableCachePolicies():
            tool.manage_changeProperties(cache_policy=policy)

            ## Base
            self.failUnlessEqual(getResults({}), expected(20))

            ## Adding an item
            item_id = 'test-getResults-cache-invalidated'
            self.portal.invokeFactory('Document', item_id)
            item = self.portal[item_id]
            item.setTitle('Document test')
            item.setSubject('Test subject')
            item.reindexObject()
            self.failUnlessEqualWithParams(getResults({}), expected(21),
                                           policy=policy)

            ## Modifying it
            item.setSubject('New subject')
            item.reindexObject()
            self.failUnlessEqualWithParams(getResults({}), expected(21),
                                           policy=policy)

            ## Removing it
            self.portal.manage_delObjects([item_id])
            self.failUnlessEqualWithParams(getResults({}), expected(20),
                                           policy=policy)


    def test_cache_policies_getResults_criteria_discriminant(self):
        mtool = getToolByName(self.portal, 'portal_membership')
        mtool.addMember('member1', 'member1', ['Member'], [])
        mtool.addMember('member2', 'member2', ['Member'], [])
        mtool.addMember('manager', 'manager', ['Manager'], [])

        ftool = getToolByName(self.portal, CONF_TOOL_ID)
        getProp = ftool.getProperty
        setProp = ftool.manage_changeProperties
        setProp(left_facets=['getTitleFirstWord'],
                right_facets=[],
                meta_types=['ATDocument'])
        getResults = self._getResultsFunc()

        ## Test that the search criteria is discriminant, hopefully.
        last_results = None
        criteria_a = {}
        criteria_b = {'getTitleFirstWord': 'Documeny'}
        for policy, user, criteria in \
            (('roles', 'member1', criteria_a),
             ('roles', 'member2', criteria_b),
             ('extreme', 'member1', criteria_a),
             ('extreme', 'member2', criteria_b),
             ):
            if policy != getProp('cache_policy'):
                setProp(cache_policy=policy)
            self.login(user)
            results = getResults(criteria)
            self.failIfEqualWithParams(id(results), id(last_results),
                                       policy=policy, user=user)
            last_results = results
            self.logout()


    def test_cache_policies_getResults_cache_used(self):
        """Test that the cache is used when it should, and not used
        when it should not.
        """
        mtool = getToolByName(self.portal, 'portal_membership')
        mtool.addMember('member1', 'member1', ['Member'], [])
        mtool.addMember('member2', 'member2', ['Member'], [])
        mtool.addMember('manager', 'manager', ['Manager'], [])

        ftool = getToolByName(self.portal, CONF_TOOL_ID)
        getProp = ftool.getProperty
        setProp = ftool.manage_changeProperties
        setProp(left_facets=['getTitleFirstWord'],
                right_facets=[],
                meta_types=['ATDocument'])
        getResults = self._getResultsFunc()

        expected = lambda n: n == 0 and \
                   {'getTitleFirstWord': []} or \
                   {'getTitleFirstWord': [{'value': 'Document',
                                           'label': 'Document',
                                           'n_results': n}]}
        item_id = 'document_test'
        self.setRoles(['Manager'])
        self.portal.invokeFactory('Document', item_id)
        item = self.portal[item_id]
        item.setTitle('Document test')
        wtool = getToolByName(self.portal, 'portal_workflow')
        wtool.doActionFor(item, 'publish')
        self.setRoles([])

        last_results = None
        for policy, user, n_expected, expected_cache_used in \
            (('none', 'member1', 1, False),
             ('none', 'member2', 1, False),
             ('none', 'manager', 21, False),
             ('user', 'member1', 1, False),
             ('user', 'member2', 1, False),
             ('user', 'manager', 21, False),
             ('roles', 'member1', 1, False),
             ('roles', 'member2', 1, True),
             ('roles', 'manager', 21, False),
             ('extreme', 'member1', 1, False),
             ('extreme', 'member2', 1, True),
             ('extreme', 'manager', 1, True)):
            if policy != getProp('cache_policy'):
                setProp(cache_policy=policy)
            self.login(user)

            results = getResults({'getTitleFirstWord': 'Document'})
            self.failUnlessEqualWithParams(results, expected(n_expected),
                                           policy=policy, user=user)
            if expected_cache_used:
                self.failUnlessEqualWithParams(id(last_results), id(results),
                                               policy=policy, user=user)
            else:
                self.failIfEqualWithParams(id(last_results), id(results),
                                           policy=policy, user=user)
            last_results = results
            self.logout()


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestBrowserView))
    return suite
