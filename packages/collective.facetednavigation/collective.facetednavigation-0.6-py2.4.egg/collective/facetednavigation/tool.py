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

$Id: tool.py 25 2008-05-30 16:52:45Z damien.baty $
"""

from Globals import InitializeClass
from OFS.SimpleItem import SimpleItem
from OFS.PropertyManager import PropertyManager

from AccessControl import ClassSecurityInfo

from Products.CMFCore.utils import UniqueObject


ID = 'portal_facetednavigation'
TITLE = 'Faceted navigation tool'
META_TYPE = 'FacetedNavigationTool'


class FacetedNavigationTool(UniqueObject, SimpleItem, PropertyManager):
    """A tool that holds configuration information."""
    id = ID
    title = TITLE
    meta_type = META_TYPE

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
                   {'id': 'sort_on',
                    'label': 'Sort matching items on',
                    'mode': 'w',
                    'type': 'string'},
                   {'id': 'sort_order',
                    'label': 'Sort order (ascending or descending)',
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
    sort_on = ''
    sort_order = ''
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
        """Return facets that should appear in the left column.

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


InitializeClass(FacetedNavigationTool)
