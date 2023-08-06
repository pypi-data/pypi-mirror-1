"""GenericSetup export/import steps.

$Id: exportimport.py 73039 2008-10-05 22:04:52Z dbaty $
"""

from Products.CMFCore.utils import getToolByName

from collective.facetednavigation.tool import CATALOG_ID


PROFILE_FILE = 'collective.facetednavigation.txt'

def restrictToProfile(func):
    """A decorator that prevents ``func`` to be executed on other
    Generic Setup profiles.
    """
    def wrapper(context):
        if context.readDataFile(PROFILE_FILE) is not None:
            return func(context)
        else:
            return None
    wrapper.__name__ = func.__name__
    wrapper.__dict__.update(func.__dict__)
    wrapper.__doc__ = func.__doc__
    wrapper.__module__ = func.__module__
    return wrapper


## ``CMFCore.exportimport.catalog.importCatalogTool()`` always adds
## indexes and metadata in ``portal_catalog``. We would like to add
## them in our dedicated catalog.
@restrictToProfile
def addIndexesAndMetadata(context,
                          catalog_id=CATALOG_ID,
                          indexes=[('allowedRolesAndUsers', 'KeywordIndex')],
                          columns=['getIcon', 'Title']):
    """Add ``indexes`` and ``columns`` (metadata) to the specified
    catalog.
    """
    site = context.getSite()
    catalog = getToolByName(site, catalog_id)
    for name, meta_type in indexes:
        catalog.addIndex(name, meta_type)
    for column in columns:
        catalog.addColumn(column)
