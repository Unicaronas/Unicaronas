from ..result import Result
from ..query import SearchQuery


class BaseThirdPartySearch(object):

    def __init__(self, connection):
        self._connection = connection

    def get_connection(self):
        """Retrieves a connection object
        to the resource
        """
        return self._connection

    def search(self, query):
        """Returns ordered trips based
        on the query
        """
        assert isinstance(query, SearchQuery)
        conn = self.get_connection()
        if conn.is_expired:
            # If connection is expired, return empty results
            return Result()
        response = conn.post(query)
        return Result(response)
