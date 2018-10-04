import requests
from .exceptions import TokenExpiredError
from ..fb_search_tools import RedisCache
from ..result.base import BaseResultItem


class BaseConnection(object):

    @property
    def connection_name(self):
        raise NotImplementedError('Implement connection_name')

    @property
    def parameters(self):
        parameters = self.get_parameters()
        return parameters

    @property
    def is_expired(self):
        return False

    def get_parameters(self, query):
        raise NotImplementedError('Implement parameter get from query object')

    def get_cached_response(self, parameters):
        cache = RedisCache()
        response = cache.get_key(parameters, extend=False)
        return response

    def cache_response(self, parameters, response):
        # Cache for 10 minutes
        cache = RedisCache(timeout=600)
        cache.set_key(parameters, response)

    def send_request(self, parameters):
        # Try to get a cached version
        cached_response = self.get_cached_response(parameters)
        if cached_response is not None:
            return cached_response
        response = requests.get(**parameters)
        if response.status_code != requests.codes.ok:
            return None
        response.raise_for_status()
        json_response = response.json()
        # Cache response
        self.cache_response(parameters, json_response)
        return json_response

    def _normalize_response(self, response):
        raise NotImplementedError('Implement normalize_response')

    def normalize_response(self, response):
        """Normalize response to a list of
        ResultItems
        """
        response = self._normalize_response(response)
        assert all([isinstance(r, BaseResultItem) for r in response])
        return response

    def filter_response(self, response, query):
        """Perform additional filtering"""
        return response

    def order_response(self, response, query):
        """Perform ordering"""
        return sorted(response, key=lambda item: (item.datetime, item.price))

    def post(self, query):
        if self.is_expired:
            raise TokenExpiredError(f"Token expired")
        parameters = self.get_parameters(query)
        response = self.send_request(parameters)
        if response is None:
            return []
        response = self.normalize_response(response)
        response = self.filter_response(response, query)
        response = self.order_response(response, query)
        return response
