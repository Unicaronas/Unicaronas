from .base import BaseConnection


class BlaBlaCarConnection(BaseConnection):

    @property
    def connection_name(self):
        return 'blablacar'

    def get_parameters(self, query):
        return {}

    def normalize_response(self, response):
        return {}
