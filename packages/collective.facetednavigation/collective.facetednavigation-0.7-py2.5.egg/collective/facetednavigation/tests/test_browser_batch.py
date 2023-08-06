"""Tests for ``collective.facetednavigation.browser.utils`` module.

$Id: test_browser_batch.py 69976 2008-08-14 22:44:45Z dbaty $
"""

from unittest import TestCase

from collective.facetednavigation.browser.batch import Batch


class TestBrowserBatch(TestCase):
    """Make sure that ``browser.batch`` works."""

    def test_Batch(self):
        ## Default value (unless specified)
        batch_length=10
        batch_n_pages = 5

        ## Bogus value for ``current``
        items = [1]
        self.failUnlessRaises(ValueError, Batch, items, current=0)
        self.failUnlessRaises(ValueError, Batch, items, current=2)

        ## 0 items, page 1
        items = []
        batch = Batch(items,
                      batch_length=batch_length,
                      batch_n_pages=batch_n_pages,
                      current=1)
        self.failUnlessEqual(batch.total_length, 0)
        self.failUnlessEqual(list(batch), [])
        self.failUnlessEqual(list(batch.slice), [])
        self.failUnlessEqual(batch.current, 1)
        self.failUnlessEqual(batch.pages, [])
        self.failUnlessEqual(batch.previous, None)
        self.failUnlessEqual(batch.next, None)

        ## 10 items, page 1
        items = range(1, 11)
        batch = Batch(items,
                      batch_length=batch_length,
                      batch_n_pages=batch_n_pages,
                      current=1)
        self.failUnlessEqual(batch.total_length, 10)
        self.failUnlessEqual(list(batch), items)
        self.failUnlessEqual(list(batch.slice), range(1, 11)) ## 1..10
        self.failUnlessEqual(batch.current, 1)
        self.failUnlessEqual(batch.pages, [1])
        self.failUnlessEqual(batch.previous, None)
        self.failUnlessEqual(batch.next, None)

        ## 20 items, page 1
        items = range(1, 21)
        batch = Batch(items,
                      batch_length=batch_length,
                      batch_n_pages=batch_n_pages,
                      current=1)
        self.failUnlessEqual(batch.total_length, 20)
        self.failUnlessEqual(list(batch), items)
        self.failUnlessEqual(list(batch.slice), range(1, 11)) ## 1..10
        self.failUnlessEqual(batch.current, 1)
        self.failUnlessEqual(batch.pages, [1, 2])
        self.failUnlessEqual(batch.previous, None)
        self.failUnlessEqual(batch.next, 2)

        ## 20 items, page 2
        items = range(1, 21)
        batch = Batch(items,
                      batch_length=batch_length,
                      batch_n_pages=batch_n_pages,
                      current=2)
        self.failUnlessEqual(batch.total_length, 20)
        self.failUnlessEqual(list(batch), items)
        self.failUnlessEqual(list(batch.slice), range(11, 21)) ## 11..21
        self.failUnlessEqual(batch.current, 2)
        self.failUnlessEqual(batch.pages, [1, 2])
        self.failUnlessEqual(batch.previous, 1)
        self.failUnlessEqual(batch.next, None)

        ## 21 items, page 1
        items = range(1, 22)
        batch = Batch(items,
                      batch_length=batch_length,
                      batch_n_pages=batch_n_pages,
                      current=1)
        self.failUnlessEqual(batch.total_length, 21)
        self.failUnlessEqual(list(batch), items)
        self.failUnlessEqual(list(batch.slice), range(1, 11)) ## 1..10
        self.failUnlessEqual(batch.current, 1)
        self.failUnlessEqual(batch.pages, [1, 2, 3])
        self.failUnlessEqual(batch.previous, None)
        self.failUnlessEqual(batch.next, 2)

        ## 21 items, page 2
        items = range(1, 22)
        batch = Batch(items,
                      batch_length=batch_length,
                      batch_n_pages=batch_n_pages,
                      current=2)
        self.failUnlessEqual(batch.total_length, 21)
        self.failUnlessEqual(list(batch), items)
        self.failUnlessEqual(list(batch.slice), range(11, 21)) ## 11..20
        self.failUnlessEqual(batch.current, 2)
        self.failUnlessEqual(batch.pages, [1, 2, 3])
        self.failUnlessEqual(batch.previous, 1)
        self.failUnlessEqual(batch.next, 3)

        ## 100 items, page 1
        items = range(1, 101)
        batch = Batch(items,
                      batch_length=10,
                      batch_n_pages=5,
                      current=1)
        self.failUnlessEqual(batch.total_length, 100)
        self.failUnlessEqual(list(batch), items)
        self.failUnlessEqual(list(batch.slice), range(1, 11)) ## 1..10
        self.failUnlessEqual(batch.current, 1)
        self.failUnlessEqual(batch.pages, [1, 2, 3, 4, 5])
        self.failUnlessEqual(batch.previous, None)
        self.failUnlessEqual(batch.next, 2)

        ## 100 items, page 2
        items = range(1, 101)
        batch = Batch(items,
                      batch_length=10,
                      batch_n_pages=5,
                      current=2)
        self.failUnlessEqual(batch.total_length, 100)
        self.failUnlessEqual(list(batch), items)
        self.failUnlessEqual(list(batch.slice), range(11, 21)) ## 11..20
        self.failUnlessEqual(batch.current, 2)
        self.failUnlessEqual(batch.pages, [1, 2, 3, 4, 5])
        self.failUnlessEqual(batch.previous, 1)
        self.failUnlessEqual(batch.next, 3)

        ## 100 items, page 5
        items = range(1, 101)
        batch = Batch(items,
                      batch_length=10,
                      batch_n_pages=5,
                      current=5)
        self.failUnlessEqual(batch.total_length, 100)
        self.failUnlessEqual(list(batch), items)
        self.failUnlessEqual(list(batch.slice), range(41, 51)) ## 41..50
        self.failUnlessEqual(batch.current, 5)
        self.failUnlessEqual(batch.pages, [3, 4, 5, 6, 7])
        self.failUnlessEqual(batch.previous, 4)
        self.failUnlessEqual(batch.next, 6)

        ## 100 items, page 7
        items = range(1, 101)
        batch = Batch(items,
                      batch_length=10,
                      batch_n_pages=5,
                      current=7)
        self.failUnlessEqual(batch.total_length, 100)
        self.failUnlessEqual(list(batch), items)
        self.failUnlessEqual(list(batch.slice), range(61, 71)) ## 61..70
        self.failUnlessEqual(batch.current, 7)
        self.failUnlessEqual(batch.pages, [5, 6, 7, 8, 9])
        self.failUnlessEqual(batch.previous, 6)
        self.failUnlessEqual(batch.next, 8)

        ## 100 items, page 9
        items = range(1, 101)
        batch = Batch(items,
                      batch_length=10,
                      batch_n_pages=5,
                      current=9)
        self.failUnlessEqual(batch.total_length, 100)
        self.failUnlessEqual(list(batch), items)
        self.failUnlessEqual(list(batch.slice), range(81, 91)) ## 81..90
        self.failUnlessEqual(batch.current, 9)
        self.failUnlessEqual(batch.pages, [6, 7, 8, 9, 10])
        self.failUnlessEqual(batch.previous, 8)
        self.failUnlessEqual(batch.next, 10)

        ## 100 items, page 10
        items = range(1, 101)
        batch = Batch(items,
                      batch_length=10,
                      batch_n_pages=5,
                      current=10)
        self.failUnlessEqual(batch.total_length, 100)
        self.failUnlessEqual(list(batch), items)
        self.failUnlessEqual(list(batch.slice), range(91, 101)) ## 91..100
        self.failUnlessEqual(batch.current, 10)
        self.failUnlessEqual(batch.pages, [6, 7, 8, 9, 10])
        self.failUnlessEqual(batch.previous, 9)
        self.failUnlessEqual(batch.next, None)


def test_suite():
    import zope.testing.doctest
    from unittest import makeSuite
    from unittest import TestSuite
    from collective.facetednavigation.browser import batch

    suite = TestSuite()
    suite.addTest(makeSuite(TestBrowserBatch))
    suite.addTest(zope.testing.doctest.DocTestSuite(batch))
    return suite
