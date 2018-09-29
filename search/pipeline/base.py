from ..finder.base import BaseFinder
from ..term import Term


class BasePipeline(object):

    def __init__(self, steps):
        assert isinstance(steps, list)
        assert all([isinstance(step, BaseFinder) for step in steps])
        self._steps = steps

    @property
    def steps(self):
        return self._steps

    def search(self, query):
        """Search
        Run through all steps trying to find a match for the query
        For each step, transform the query and then try searching
        If no result is found, go to the next step.
        If a result is found, go back the pipeline caching the result and return it.
        If at the end of the pipeline and no result was found, return None
        """
        assert isinstance(query, str)

        term = Term(query)

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

            # No need to go further into the steps
            break
        return result
