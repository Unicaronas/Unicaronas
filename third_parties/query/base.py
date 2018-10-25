from django.http import HttpRequest
from search.term.base import BaseTerm
from datetime import datetime
from rest_framework.request import Request


class BaseSearchQuery(object):

    def __init__(self, origin, destination, price_lte, datetime_lte, datetime_gte, request):
        assert isinstance(origin, BaseTerm)
        assert isinstance(destination, BaseTerm)
        assert isinstance(price_lte, int)
        assert isinstance(datetime_gte, datetime)
        assert isinstance(datetime_lte, datetime)
        assert isinstance(request, (HttpRequest, Request, type(None)))
        self._origin = origin
        self._destination = destination
        self._price_lte = price_lte
        self._datetime_lte = datetime_lte
        self._datetime_gte = datetime_gte
        self._request = request

    @property
    def origin(self):
        return self._origin

    @property
    def destination(self):
        return self._destination

    @property
    def price_lte(self):
        return self._price_lte

    @property
    def datetime_gte(self):
        return self._datetime_gte

    @property
    def datetime_lte(self):
        return self._datetime_lte

    @property
    def request(self):
        return self._request

    @property
    def user(self):
        return self.request.user

    @property
    def app(self):
        return self.request.auth.application

    @property
    def path_info(self):
        return self.request.path_info

    @property
    def full_path_info(self):
        return self.request.get_full_path_info()

    @property
    def method(self):
        return self.request.method
