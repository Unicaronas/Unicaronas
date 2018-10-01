from datetime import datetime
from search.term import Term
from search.finder import SynonymFinder
from ..search.base import BaseThirdPartySearch
from ..query import SearchQuery
from ..result import Result


class BasePipeline(object):

    def __init__(self, steps):
        assert isinstance(steps, list)
        assert all([isinstance(step, BaseThirdPartySearch) for step in steps])
        self._steps = steps

    @property
    def steps(self):
        return self._steps

    def search(self, origin, destination, price_lte, datetime_lte, datetime_gte, request):
        assert isinstance(origin, str)
        assert isinstance(destination, str)
        assert isinstance(price_lte, int)
        assert isinstance(datetime_lte, datetime)
        assert isinstance(datetime_gte, datetime)

        origin = Term(origin, 'both', request)
        destination = Term(destination, 'both', request)

        origin = SynonymFinder().transform(origin)
        destination = SynonymFinder().transform(destination)

        query = SearchQuery(origin, destination, price_lte, datetime_lte, datetime_gte, request)

        steps = self.steps

        results = Result()

        for i, step in enumerate(steps):
            results += step.search(query)

        return results
