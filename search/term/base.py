class BaseTerm(object):

    def __init__(self, query):
        assert isinstance(query, str)
        self._query = query
        self._original_query = query

    @property
    def query(self):
        """Return the query term"""
        return self._query.lower()

    @property
    def original_query(self):
        """Original query, before any transformations"""
        return self._original_query.lower()

    @property
    def is_transformed(self):
        """Whether or not the query was transformed"""
        return self._original_query != self._query

    def transform(self, transformed):
        """Transform the query"""
        assert isinstance(transformed, str)
        self._query = transformed
        return self

    def __repr__(self):
        return str(self)

    def __str__(self):
        return f"Term: {self.query}"
