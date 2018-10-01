from .base import BaseConnection


class FacebookConnection(BaseConnection):

    @property
    def connection_name(self):
        return 'facebook'

    def get_parameters(self, query):
        return {}

    def normalize_response(self, response):
        return {}
