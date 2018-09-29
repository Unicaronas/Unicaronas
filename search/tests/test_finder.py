from django.contrib.gis.geos.collections import Point
from django.test import TestCase
from ..term import Term
from ..result import Result
from ..finder.base import BaseFinder, BaseCacheFinder
from ..finder import LocalCacheFinder


class BaseFinderTestCase(TestCase):
    def set_finders(self):
        self.finder1 = BaseFinder()
        self.finder2 = BaseFinder()

    def setUp(self):
        self.term1 = Term("minha query")
        self.term2 = Term("minha outra query")
        self.res1 = Result('query', 'addr', Point(1, 2))
        self.res2 = Result('outra query', 'outro addr', Point(1, 2))
        self.res2 = Term("minha outra query")
        self.set_finders()

    def test_transform_input_output(self):
        with self.assertRaises(AssertionError):
            self.finder1.transform('str')

    def test_search_input_output(self):
        with self.assertRaises(AssertionError):
            self.finder1.search('str')

    def test_cache_input_output(self):
        with self.assertRaises(AssertionError):
            self.finder1.cache('str')

    def test_hit_input_output(self):
        with self.assertRaises(AssertionError):
            self.finder1.hit('str')

    def test_transform(self):
        r = self.finder1.transform(self.term1)
        self.assertIsInstance(r, Term)
        r2 = self.finder2.transform(self.term2)
        self.assertIsInstance(r2, Term)
        self.assertEqual(r.query, self.term1)
        self.assertEqual(r2.query, self.term2)

    def test_search(self):
        r = self.finder1.search(self.term1)
        self.assertIsNone(r)
        r2 = self.finder2.search(self.term2)
        self.assertIsNone(r2)

    def test_cache(self):
        self.finder1.cache(self.res1)
        self.finder2.cache(self.res2)

    def test_hit(self):
        self.finder1.hit(self.term1)
        self.finder2.hit(self.term2)


class BaseCacheFinderTestCase(BaseFinderTestCase, TestCase):
    def set_finders(self):
        self.finder1 = BaseCacheFinder()
        self.finder2 = BaseCacheFinder()

    def test_encode(self):
        self.assertEqual(self.finder1.encode("term"), "term")

    def test_decode(self):
        self.assertEqual(self.finder1.decode("raw"), "raw")


class LocalCacheFinderTestCase(BaseCacheFinderTestCase, TestCase):
    def set_finders(self):
        self.finder1 = LocalCacheFinder()
        self.finder2 = LocalCacheFinder()

        # TODO: Finish this
