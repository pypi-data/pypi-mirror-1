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
"""Various utility classes and functions.

$Id: utils.py 69976 2008-08-14 22:44:45Z dbaty $
"""

from Products.PageTemplates.PageTemplate import PageTemplate


def renderTemplateMacro(context, template, macro, namespace={}):
    """Render the given ``macro`` of the given ``template``."""
    t = PageTemplate()
    t.write(u'<metal:block use-macro="context/%s/macros/%s"/>' %\
            (template, macro))
    namespace = namespace.copy()
    namespace.setdefault('context', context)
    return t.pt_render(extra_context=namespace)
