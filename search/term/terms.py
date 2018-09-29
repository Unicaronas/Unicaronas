from django.http import HttpRequest
from .base import BaseTerm


class Term(BaseTerm):

    def __init__(self, query, query_type=None, request=None):
        assert isinstance(request, (HttpRequest, type(None)))
        assert isinstance(query_type, (str, type(None)))
        self._request = request
        self._query_type = query_type
        super().__init__(query)

    @property
    def request(self):
        # Query request object
        return self._request

    @property
    def query_type(self):
        # If it is a query for the origin or destination
        return self._query_type
