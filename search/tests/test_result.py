from django.test import TestCase
from django.contrib.gis.geos.collections import Point
from ..result import Result
from ..result.base import BaseResult


class BaseResultTestCase(TestCase):

    def setUp(self):
        self.res1 = BaseResult("query", "addr", Point(1, 2))
        self.res2 = BaseResult("outro query", "outro addr", Point(3, 4))

    def test_parameters(self):
        with self.assertRaises(TypeError):
            Result(None)
        with self.assertRaises(TypeError):
            Result("str", None)
        with self.assertRaises(AssertionError):
            Result("str", 'str', None)
        with self.assertRaises(AssertionError):
            Result("str", 'str', "str")
        with self.assertRaises(AssertionError):
            Result("str", None, Point(1, 2))
        with self.assertRaises(AssertionError):
            Result(None, 'str', Point(1, 2))

    def test_query(self):
        self.assertEqual(self.res1.query, 'query')
        self.assertEqual(self.res2.query, 'outro query')

    def test_address(self):
        self.assertEqual(self.res1.address, 'addr')
        self.assertEqual(self.res2.address, 'outro addr')

    def test_point(self):
        self.assertEqual(self.res1.point, Point(1, 2))
        self.assertEqual(self.res2.point, Point(3, 4))

    def test_coords(self):
        self.assertEqual(self.res1.coords, (1, 2))
        self.assertEqual(self.res2.coords, (3, 4))

    def test_latitude(self):
        self.assertEqual(self.res1.latitude, 1)
        self.assertEqual(self.res1.longitude, 2)
        self.assertEqual(self.res2.latitude, 3)
        self.assertEqual(self.res2.longitude, 4)

    def test_dict_coords(self):
        self.assertEqual(self.res1.dict_coords, {'latitude': 1, 'longitude': 2})
        self.assertEqual(self.res2.dict_coords, {'latitude': 3, 'longitude': 4})


class ResultTestCase(BaseResultTestCase, TestCase):
    pass
