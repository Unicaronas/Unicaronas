from .base import BasePipeline
from ..finder import SynonymFinder, LocalCacheFinder, RedisFinder, GoogleAPIFinder, DBFinder
from ..term import Term


class Pipeline(BasePipeline):
    """Pipelines finders"""


class DefaultPipeline(BasePipeline):

    def __init__(self):
        steps = [
            SynonymFinder(), LocalCacheFinder(),
            RedisFinder(), DBFinder(), GoogleAPIFinder()
        ]
        super().__init__(steps)


class RequestPipeline(DefaultPipeline):

    def __init__(self, query_type=None, request=None):
        self._request = request
        self._query_type = query_type
        super().__init__()

    @property
    def request(self):
        return self._request

    @property
    def query_type(self):
        return self._query_type

    def search(self, query):
        """Search
        Run through all steps trying to find a match for the query
        For each step, transform the query and then try searching
        If no result is found, go to the next step.
        If a result is found, go back the pipeline caching the result and return it.
        If at the end of the pipeline and no result was found, return None.

        After term was found and cached, propagate hits upward
        """
        assert isinstance(query, str)

        term = Term(query, query_type=self.query_type, request=self.request)

        steps = self.steps
        # For each step
        for i, step in enumerate(steps):
            term = step.transform(term)
            result = step.search(term)
            # If no result was found
            if result is None:
                # Go to the next step
                continue
            # If a result was found, go back the pipeline
            for back_step in steps[i - 1::-1]:
                back_step.cache(result)
            # Propagate hits upward
            for foward_step in steps[i:]:
                foward_step.hit(term)

            # No need to go further into the steps
            break

        return result
