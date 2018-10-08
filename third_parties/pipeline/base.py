from datetime import datetime
from search.term import Term
from search.finder import TermPreparationFinder, SynonymFinder, GrammarCorrectorFinder
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

        preparation = TermPreparationFinder()
        grammar = GrammarCorrectorFinder()
        synonym = SynonymFinder()

        origin = Term(origin, 'both', request)
        destination = Term(destination, 'both', request)
        origin = preparation.transform(origin)
        destination = preparation.transform(destination)
        origin = grammar.transform(origin)
        destination = grammar.transform(destination)
        origin = synonym.transform(origin)
        destination = synonym.transform(destination)

        query = SearchQuery(origin, destination, price_lte, datetime_lte, datetime_gte, request)

        steps = self.steps

        results = Result()

        for i, step in enumerate(steps):
            results += step.search(query)

        # Sort results
        results.sort()
        return results
