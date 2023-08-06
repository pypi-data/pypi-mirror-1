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
"""A tool that stores configuration information.

$Id: tool.py 73039 2008-10-05 22:04:52Z dbaty $
"""

from zope.component import queryUtility
from zope.app.cache.interfaces.ram import IRAMCache

from Globals import InitializeClass
from OFS.SimpleItem import SimpleItem
from OFS.PropertyManager import PropertyManager
from AccessControl import ClassSecurityInfo
from AccessControl.Permissions import manage_properties


from Products.CMFCore.utils import UniqueObject

from Products.CMFPlone.CatalogTool import CatalogTool


CATALOG_ID = 'portal_facets_catalog' ## Cf. "profiles/default/toolset.xml"
CONF_TOOL_ID = 'portal_facetednavigation'


class FacetsCatalogTool(CatalogTool):
    """A straightforward subclass of Plone ``CatalogTool``, only
    needed because we do not want our tool to be called
    ``portal_catalog``.
    """
    id = CATALOG_ID


class FacetedNavigationTool(UniqueObject, SimpleItem, PropertyManager):
    """A tool that holds configuration information."""

    id = CONF_TOOL_ID
    title = 'Faceted navigation tool'
    meta_type = 'FacetedNavigationTool'

    security = ClassSecurityInfo()
    decProtected = security.declareProtected

    manage_options = (PropertyManager.manage_options
                      + SimpleItem.manage_options)

    _properties = ({'id': 'meta_types',
                    'label': 'Meta types to include',
                    'mode': 'w',
                    'type': 'lines'},
                   {'id': 'left_facets',
                    'label': 'List of facets (left column)',
                    'mode': 'w',
                    'type': 'lines'},
                   {'id': 'right_facets',
                    'label': 'List of facets (right column)',
                    'mode': 'w',
                    'type': 'lines'},
                   {'id': 'default_criteria',
                    'label': 'Default search criteria',
                    'mode': 'w',
                    'type': 'lines'},
                   {'id': 'sort_on',
                    'label': 'Sort matching items on',
                    'mode': 'w',
                    'type': 'string'},
                   {'id': 'sort_order',
                    'label': 'Sort order (ascending or descending)',
                    'mode': 'w',
                    'type': 'string'},
                   {'id': 'cache_policy',
                    'label': 'Cache policy (user/roles/extreme)',
                    'mode': 'w',
                    'type': 'string'},
                   {'id': 'batch_length',
                    'label': 'Number of items per page (batch)',
                    'mode': 'w',
                    'type': 'int'},
                   {'id': 'batch_n_pages',
                    'label': 'Number of pages (batch)',
                    'mode': 'w',
                    'type': 'int'},
                   )

    meta_types = []
    left_facets = []
    right_facets = []
    default_criteria = []
    sort_on = ''
    sort_order = ''
    cache_policy = 'user'
    batch_length = 10
    batch_n_pages = 5


    decProtected('View', 'getAllFacets')
    def getAllFacets(self):
        """Return all facets as a list of mappings:

          {'id': <facet-id>,
           'label': <label>,
           'uid_attribute': <metadata>,
           'widget': <widget-name>}
        """
        return self.getLeftFacets() + self.getRightFacets()


    decProtected('View', 'getLeftFacets')
    def getLeftFacets(self):
        """Return facets that should appear in the left column.

        See ``getAllFacets()`` for the format.
        """
        return self._getFacetsForColumn('left')


    decProtected('View', 'getRightFacets')
    def getRightFacets(self):
        """Return facets that should appear in the right column.

        See ``getAllFacets()`` for the format.
        """
        return self._getFacetsForColumn('right')


    def _getFacetsForColumn(self, column):
        """Return facets that should appear in the given column.

        See ``getAllFacets()`` for the format.
        """
        lines = self.getProperty(column + '_facets')
        facets = []
        for line in lines:
            values = line.split(';')
            values.extend((None, ) * (4 - len(values)))
            facet_id, label, uid_attribute, widget = values
            if not label:
                label = facet_id
            if not uid_attribute:
                uid_attribute = None
            if not widget:
                widget = 'checkboxes'
            facets.append({'id': facet_id,
                           'label': label,
                           'uid_attribute': uid_attribute,
                           'widget': widget})
        return facets


    decProtected('View', 'getLeftFacets')
    def getDefaultCriteria(self):
        """Return default search criteria."""
        criteria = {}
        for line in self.getProperty('default_criteria'):
            index, value = line.split(';')
            criteria[index] = value
        return criteria


    security.declareProtected(manage_properties,
                              'manage_changeProperties')
    def manage_changeProperties(self, **kwargs):
        """Call original overriden method but also invalidate the
        cache (see ``_invalidateCache()``).
        """
        self._invalidateCache()
        return PropertyManager.manage_changeProperties(self, **kwargs)


    def _invalidateCache(self):
        """Invalidate the cache for ``getResults()`` since it depends
        on some configuration of this tool (list of meta_types,
        default criteria, etc.).
        """
        cache = queryUtility(IRAMCache)
        cache.invalidate('collective.facetednavigation.browser.facetednavigation.getResults')


    def _getAvailableCachePolicies(self):
        return ('none', 'user', 'roles', 'extreme')


InitializeClass(FacetedNavigationTool)
