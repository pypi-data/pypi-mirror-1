"""Define a base class and prepare ZopeTestCase and PloneTestCase to
be used by our tests.

$Id: base.py 20 2008-05-08 09:14:39Z damien.baty $
"""

from Testing import ZopeTestCase

from Products.PloneTestCase import PloneTestCase

from zope.interface import directlyProvides
from zope.annotation.interfaces import IAttributeAnnotatable
from zope.publisher.browser import TestRequest as BaseTestRequest


PRODUCT = 'collective.facetednavigation'
ZopeTestCase.installProduct(PRODUCT)
PloneTestCase.setupPloneSite(products=[PRODUCT])


class TestRequest(BaseTestRequest):
    """Equivalent to ``zope.publisher.browser.TestRequest`` with a
    ``set``method.
    """
    def set(self, attr, value):
        setattr(self, attr, value)


class FacetedNavigationTestCase(PloneTestCase.PloneTestCase):

    def _getNewRequest(self, session={}):
        """Return an annotable test request, with the given session."""
        request = TestRequest()
        request.SESSION = session
        ## We need to make the request annotable (for 'memoize.view')
        directlyProvides(request, IAttributeAnnotatable)
        return request
