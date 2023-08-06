# This file is part of Faceted Navigation.
#
# Copyright (c) 2008 by ENA (http://www.ena.fr)
# 
# Faceted Navigation is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License as
# published by the Free Software Foundation; either version 2 of the
# License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307
# USA
#
"""Browser view for faceted navigation.

$Id: facetednavigation.py 73039 2008-10-05 22:04:52Z dbaty $
"""

import logging
from types import ListType
from types import TupleType

from Products.Five import BrowserView
from Missing import MV as MissingValue
from AccessControl import getSecurityManager

from Products.ZCatalog.Catalog import CatalogError

from Products.CMFCore.utils import getToolByName

from plone import memoize

from kss.core import KSSView
from kss.core import kssaction

from collective.facetednavigation.tool import CATALOG_ID
from collective.facetednavigation.tool import CONF_TOOL_ID
from collective.facetednavigation.browser.batch import Batch
from collective.facetednavigation.browser.utils import renderTemplateMacro


MAIN_SESSION_KEY = 'faceted_navigation'
CACHE_SESSION_KEY = 'faceted_navigation_cache'
HIDDEN_FACETS_SESSION_KEY = 'faceted_navigation_hidden_facets'


def getSelectedCriteria(request):
    """Return selected criteria of this request."""
    return request.SESSION.get(MAIN_SESSION_KEY, {})


class KSSFacetedActions(KSSView):
    """A class that holds all KSS actions related to faceted navigation."""

    @kssaction
    def selectValue(self, checkbox_id):
        """Handler called when a box is checked in the faceted
        navigation template.
        """
        facet, value = checkbox_id.split('-', 1)

        ## Update session
        fn_session = getSelectedCriteria(self.request)
        values = fn_session.get(facet, [])
        if value in values:
            values.remove(value)
        else:
            values.append(value)
        fn_session[facet] = values
        if not fn_session[facet]:
            del fn_session[facet] ## We do not want empty criteria.
        session = self.request.SESSION
        session[MAIN_SESSION_KEY] = fn_session
        self.request.SESSION = session

        self.updateAllFacetBlocks()
        self.updateListOfMatchingItems()


    @kssaction
    def resetSelection(self):
        """Handler called when the user resets its selection."""
        session = self.request.SESSION
        session[MAIN_SESSION_KEY] = {}
        self.request.SESSION = session
        self.updateAllFacetBlocks()
        self.updateListOfMatchingItems()


    @kssaction
    def showOrHideFacetBlock(self, facet_id):
        """Handler called when an user wants to show/hide a facet
        block.
        """
        hidden_facets = self.request.SESSION.get(HIDDEN_FACETS_SESSION_KEY, [])
        if facet_id in hidden_facets:
            hidden_facets.remove(facet_id)
        else:
            hidden_facets.append(facet_id)
        self.request.SESSION[HIDDEN_FACETS_SESSION_KEY] = hidden_facets


    @kssaction
    def showBatchPage(self, batch_page):
        batch_page = int(batch_page.split('-')[1]) ## 'batch-<batch_page>'
        self.updateListOfMatchingItems(batch_page)


    def updateAllFacetBlocks(self):
        """Update all facet blocks."""
        view = FacetedNavigation(self.context, self.request)
        for facet in view.getAllFacets():
            self.updateFacetBlock(facet, view)


    def updateFacetBlock(self, facet, view=None):
        """Update the block corresponding to the given facet.

        If ``view`` is not ``None``, it should be a
        ``FacetedNavigation`` instance. Otherwise, it is constructed.

        The block is updated only if it has to. If it is already up to
        date, nothing is done browser-side.
        """
        if view is None:
            view = FacetedNavigation(self.context, self.request)

        ## Make sure that we really need to update this block.
        results = view.getResults()[facet['id']]
        cache = self.request.SESSION.get(CACHE_SESSION_KEY, {})
        if results == cache.get(facet['id'], None):
            return ## This facet block is up to date. Do nothing.

        ## We really need to update this block.
        if not self.request.SESSION.has_key(CACHE_SESSION_KEY):
            self.request.SESSION[CACHE_SESSION_KEY] = {}
        self.request.SESSION[CACHE_SESSION_KEY][facet['id']] = results

        ksscore = self.getCommandSet('core')
        block = ksscore.getHtmlIdSelector(facet['id'])
        html = renderTemplateMacro(self.context,
                                   '@@faceted-navigation-macros',
                                   'display-facet',
                                   namespace={'facet': facet,
                                              'view': view,
                                              'request': self.request})
        ksscore.replaceHTML(block, html)


    def updateListOfMatchingItems(self, batch_current_page=1):
        """Update list of matching items."""
        ksscore = self.getCommandSet('core')
        self.request.set('batch_current_page', batch_current_page)
        view = FacetedNavigation(self.context, self.request)
        html = renderTemplateMacro(self.context,
                                   '@@faceted-navigation-macros',
                                   'display-items',
                                   namespace={'items': view.getMatchingItems(),
                                              'request': self.request})
        block = ksscore.getHtmlIdSelector('items')
        ksscore.replaceInnerHTML(block, html)


class FacetedNavigation(BrowserView):
    """A browser view which is responsible for searching the catalog
    and return items that match the criteria selected through the
    faceted navigation.
    """

    def _getConfiguration(self):
        """Return configuration tool."""
        return getToolByName(self.context, CONF_TOOL_ID)


    def getLeftFacets(self):
        return self._getConfiguration().getLeftFacets()


    def getRightFacets(self):
        return self._getConfiguration().getRightFacets()


    def getAllFacets(self):
        return self._getConfiguration().getAllFacets()


    def showFacet(self, facet_id):
        """Return whether the box for the given facet should be shown
        to the current user in the current session.
        """
        hidden = self.request.SESSION.get(HIDDEN_FACETS_SESSION_KEY, ())
        return facet_id not in hidden


    def valueIsSelected(self, facet_id, value):
        """Return whether the given value of this facet has been
        selected by the current user in the current session.
        """
        session = getSelectedCriteria(self.request)
        return value in session.get(facet_id, ())


    def _getCriteria(self):
        """Return search search criteria (by merging user-selected
        and default criteria).
        """
        criteria = getSelectedCriteria(self.request).copy()

        for facet, value in criteria.items():
            criteria[facet] = {'query': value,
                               'operator': 'and'}

        config = self._getConfiguration()
        config_values = {'meta_type': config.getProperty('meta_types'),
                         'sort_on': config.getProperty('sort_on'),
                         'sort_order': config.getProperty('sort_order')}
        for key, value in config_values.items():
            if value:
                criteria[key] = value
        criteria.update(config.getDefaultCriteria())

        return criteria


    ## FIXME: Should we ramcache 'getMatchingItems()'?
    @memoize.view.memoize
    def getMatchingItems(self):
        """Return items that match user-selected criteria."""
        criteria = self._getCriteria()
        catalog = getToolByName(self.context, CATALOG_ID)
        try:
            items = catalog.searchResults(**criteria)
        except CatalogError, exc:
            ## Some indexes cannot be used as sort indexes. Among them
            ## is 'Title', which would be quite convenient here. To
            ## work around that, we sort items ourselves.
            if 'is not capable of being used as a sort index' not in str(exc):
                raise
            sort_on = criteria['sort_on']
            del criteria['sort_on']
            sort_order = 'ascending'
            if criteria.has_key('sort_order'):
                sort_order = criteria['sort_order']
                del criteria['sort_order']
            ## Casting to a 'list' is probably not very efficient
            items = list(catalog.searchResults(**criteria))
            reverse = sort_order.lower() in ('reverse', 'descending')
            items.sort(key=lambda x: getattr(x.aq_base, sort_on),
                       reverse=reverse)

        ftool = self._getConfiguration()
        return Batch(items,
                     ftool.getProperty('batch_length'),
                     ftool.getProperty('batch_n_pages'),
                     self.request.get('batch_current_page', 1))


    ## We cannot use 'memoize.forever' because it is not thread-safe.
    def cache_key_getLabelOf(func, self, uid, attr):
        return (uid, attr)

    @memoize.ram.cache(cache_key_getLabelOf)
    def getLabelOf(self, uid, attr):
        """Return a label for the object whose UID is ``uid``.

        Since the definition of label may depend on the the type of
        the object, this method uses ``attr`` as the brain attribute
        to use.
        """
        catalog = getToolByName(self.context, CATALOG_ID)
        brains = catalog.searchResults(UID=uid)
        assert(len(brains) <= 1)
        if not brains:
            logging.info('Could not find any object with UID "%s".', uid)
            return '<unknown (%s)>' % str(uid)
        return getattr(brains[0], attr)


    def cache_key_getResults(func, self):
        """Cache function for ``getResults()``."""
        ftool = self._getConfiguration()
        policy = ftool.getProperty('cache_policy')
        if policy in ('extreme', 'roles', 'user'):            
            catalog = getToolByName(self.context, CATALOG_ID)
            criteria = getSelectedCriteria(self.request)
            if policy == 'extreme':
                cache_key = (catalog.getCounter(), criteria)
            elif policy == 'roles':
                roles = getSecurityManager().getUser().getRoles()
                cache_key = (catalog.getCounter(), criteria, roles)
            else: ## policy == 'user':
                userid = getSecurityManager().getUser().getId()
                cache_key = (catalog.getCounter(), criteria, userid)
        else: ## No cache
            ## Here, we want something unique to mimic the absence of
            ## cache. I could use 'self' but... well, it is not that
            ## unique: successive calls may reuse the same memory
            ## emplacement and therefore return the same cache key.
            ftool._invalidateCache()
            cache_key = 2
        return cache_key


    @memoize.view.memoize
    @memoize.ram.cache(cache_key_getResults)
    def getResults(self):
        """Return a mapping of the items that match the user-select
        criteria.

        This methods uses ``getMatchingItems()`` and arranges the
        result as a mapping which looks like::

            {<facet>: <list-of-results>,
             <facet-2>: <other-list-of-results>}

        where ``<facet>`` is one of the configured facets, and
        ``<list-of-results>`` is an ordered list of mappings::

            ({'value': <value>,
              'label': <label>,
              'n_results': <number-of-matching-results>}, ...)

        This list is ordered by the ``n_results`` key, and then by
        ``label`` key.
        """
        facets = self.getAllFacets()

        ## Build raw results table
        raw_results = {}
        for facet_info in facets:
            raw_results[facet_info['id']] = {}

        for brain in self.getMatchingItems():
            for facet_info in facets:
                facet = facet_info['id']
                try:
                    value = getattr(brain.aq_base, facet)
                except AttributeError:
                    logging.info('Could not find metadata "%s" for '\
                                 'brain at "%s".',
                                 facet, brain.getURL(1))
                    continue
                if value == MissingValue:
                    continue ## No index value for this object
                if type(value) not in (ListType, TupleType, type(set())):
                    value = [value]
                for v in value:
                    raw_results[facet][v] = raw_results[facet].get(v, 0) + 1

        ## Build results table that will be used by the template
        results = {}
        for facet_info in facets:
            facet = facet_info['id']
            partial = []
            for value, n_results in raw_results[facet].items():
                item = {'value': value,
                        'n_results': n_results}
                uid_attribute = facet_info.get('uid_attribute')
                if uid_attribute:
                    item['label'] = self.getLabelOf(value, uid_attribute)
                else:
                    item['label'] = value
                partial.append(item)
            partial.sort(lambda x, y: cmp(y['n_results'], x['n_results']) or \
                         cmp(x['label'], y['label']))
            results[facet] = partial

        return results
