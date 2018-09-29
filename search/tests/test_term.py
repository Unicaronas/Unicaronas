from django.http import HttpRequest
from django.test import TestCase
from ..term.base import BaseTerm
from ..term import Term


class BaseTermTestCase(TestCase):
    def setUp(self):
        self.term1 = BaseTerm("meu termo")
        self.term2 = BaseTerm("meu outro termo")

    def test_wrong_initalization(self):
        with self.assertRaises(AssertionError):
            BaseTerm(['not', 'string'])

    def test_query(self):
        self.assertEqual(self.term1.query, "meu termo")
        self.assertEqual(self.term2.query, "meu outro termo")

    def test_transform(self):
        with self.assertRaises(AssertionError):
            self.term1.transform(['not', 'string'])
        self.term1.transform('termo transformado')
        self.assertEqual(self.term1.query, "termo transformado")
        self.assertEqual(self.term1.original_query, "meu termo")


class TermTestCase(BaseTermTestCase, TestCase):
    def setUp(self):
        self.term1 = Term("meu termo")
        self.term2 = Term("meu outro termo", query_type="origin")
        self.term3 = Term("outro termo meu", request=HttpRequest())

    def test_wrong_initalization(self):
        with self.assertRaises(AssertionError):
            Term(['not', 'string'])

        with self.assertRaises(AssertionError):
            Term("string", query_type=['not', 'string'])

        with self.assertRaises(AssertionError):
            Term("string", request=['not', 'request'])

    def test_request(self):
        self.assertIsInstance(self.term1.request, type(None))
        self.assertIsInstance(self.term3.request, HttpRequest)

    def test_query_type(self):
        self.assertIsInstance(self.term1.query_type, type(None))
        self.assertIsInstance(self.term2.query_type, str)
