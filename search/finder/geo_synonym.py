from . import SynonymFinder, LocalCacheFinder, RedisFinder


class GeographicSynonymFinder(SynonymFinder):
    """
    Given a search term, look for synonyms
    by applying search.Pipeline and finding
    the synonym that is the closest
    """

    def find_geographic_synonym(self, term):
        """Given a term, pass it through a pipeline
        to find the geographic result.
        Then, do the same for every possible synonym
        After that, calculate the distances from each
        result and return the one with the minimum distance
        that is less than 5km
        """
        from . import GoogleAPIFinder, DBFinder
        from search.pipeline import Pipeline
        steps = [LocalCacheFinder(), RedisFinder(), DBFinder(),
                 GoogleAPIFinder()]
        pipe = Pipeline(steps)
        # Find geographic result
        result = pipe.search(term.query)
        if result is None:
            # if the result is none, there is no point in continuing
            return None
        # Find geographic results for each synonym
        synonyms = map(lambda synonym: (
            synonym, pipe.search(synonym)), self.SYNONYM_LOCATIONS)
        synonym_distances = map(lambda synonym: ((
            synonym[0],
            10
        ) if not synonym[1] else (
            synonym[0],
            result.point.distance(synonym[1].point) * 100)
        ), synonyms)
        filtered_synonym_distances = filter(lambda synonym: synonym[1] <= 5,
                                            synonym_distances
                                            )
        min_synonym = min(
            filtered_synonym_distances,
            default=None,
            key=lambda synonym: synonym[1]
        )
        return min_synonym[0] if min_synonym else None

    def find_synonym(self, term):
        """Find a synonym
        From the synonym map,
        find a match for the term
        """
        synonym_map = self.get_synonym_map()
        base = synonym_map.get(term.query, None)
        if base is not None:
            return base
        geo = self.find_geographic_synonym(term)
        return geo
