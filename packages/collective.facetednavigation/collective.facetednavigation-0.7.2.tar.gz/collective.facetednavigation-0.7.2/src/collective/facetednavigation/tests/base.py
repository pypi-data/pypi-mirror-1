"""Define a base class and prepare ZopeTestCase and PloneTestCase to
be used by our tests.

$Id: base.py 71774 2008-09-13 17:14:37Z dbaty $
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
    ``set`` method.
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


    def _constructErrorMessage(self, first, second, sign, **kwargs):
        """Helper code fo ``failUnlessEqualWithParams`` or
        ``failIfEqualWithParams``.
        """
        params = [('%s=%s') % (key, value) for \
                  key, value in kwargs.items()]
        msg = 'for %s:\n%r %s %r' % (';'.join(params),
                                     first, sign, second)
        return msg


    def failUnlessEqualWithParams(self, first, second, **kwargs):
        """Same as ``failUnlessEqual(first, second, msg)`` except that
        ``msg`` is generated with ``kwargs``.
        """
        msg = self._constructErrorMessage(first, second, '!=', **kwargs)
        return self.failUnlessEqual(first, second, msg)


    def failIfEqualWithParams(self, first, second, **kwargs):
        msg = self._constructErrorMessage(first, second, '==', **kwargs)
        return self.failIfEqual(first, second, msg)
