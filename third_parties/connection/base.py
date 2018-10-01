import requests
from ..result.base import BaseResultItem


class BaseConnection(object):

    @property
    def connection_name(self):
        raise NotImplementedError('Implement connection_name')

    @property
    def parameters(self):
        parameters = self.get_parameters()
        return parameters

    def get_parameters(self, query):
        raise NotImplementedError('Implement parameter get from query object')

    def send_request(self, parameters):
        response = requests.post(**parameters)

        response.raise_for_status()
        return response.json()

    def _normalize_response(self, response):
        raise NotImplementedError('Implement normalize_response')

    def normalize_response(self, response):
        """Normalize response to a list of
        ResultItems
        """
        response = self._normalize_response(response)
        assert all([isinstance(r, BaseResultItem) for r in response])
        return response

    def post(self, query):
        parameters = self.get_parameters(query)
        response = self.send_request(parameters)
        response = self.normalize_response(response)
        return response
