from unidecode import unidecode
from .base import BaseFinder


class TermPreparationFinder(BaseFinder):
    """
    Given a search term, make it lowercase and remove accents
    """

    def _transform(self, term):
        """Take a term, remove accents and make lowercase"""
        prepared_term = unidecode(term.query.lower())
        return self.perform_transform(term, prepared_term)
