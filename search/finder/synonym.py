from collections import OrderedDict
from .base import BaseFinder


class SynonymFinder(BaseFinder):
    """
    Given a search term, look for synonyms

    Only transforms the input into a known
    synonym
    """
    POSTO_IPIRANGA = 'posto ipiranga, unicamp'
    SP = 'sao paulo, sp'
    RODOVIARIA_TIETE = 'rodoviaria tiete, sao paulo'

    SYNONYM_LOCATIONS = (
        POSTO_IPIRANGA,
        SP,
        RODOVIARIA_TIETE
    )

    def is_synonym(self, term):
        return term.query in self.SYNONYM_LOCATIONS

    def get_synonym_map(self):
        """Get a map of synonyms
        Used on autocorrected words to find the result
        """

        s_map = [
            # Map to posto ipiranga, Barão geraldo
            ('unicamp', self.POSTO_IPIRANGA),
            ('unichamps', self.POSTO_IPIRANGA),
            ('universidade estadual de campinas', self.POSTO_IPIRANGA),
            ('unicamp, campinas', self.POSTO_IPIRANGA),

            ('posto ipiranga, unicamp', self.POSTO_IPIRANGA),
            ('posto ipiranga unicamp', self.POSTO_IPIRANGA),
            ('posto ipiranga', self.POSTO_IPIRANGA),
            ('posto da 1', self.POSTO_IPIRANGA),
            ('posto', self.POSTO_IPIRANGA),

            ('barao geraldo', self.POSTO_IPIRANGA),
            ('barao', self.POSTO_IPIRANGA),
            ('bg', self.POSTO_IPIRANGA),

            # Map to generic São Paulo, SP
            ('sao paulo, sao paulo', self.SP),
            ('sao paulo sao paulo', self.SP),
            ('sao paulo, sp', self.SP),
            ('sao paulo sp', self.SP),
            ('sao paulo', self.SP),
            ('sp', self.SP),
            ('sampa', self.SP),

            # Map to rodoviária tietê
            ('rodoviaria tiete, sao paulo', self.RODOVIARIA_TIETE),
            ('rodoviaria tiete sao paulo', self.RODOVIARIA_TIETE),
            ('rodoviaria tiete, sp', self.RODOVIARIA_TIETE),
            ('rodoviaria tiete sp', self.RODOVIARIA_TIETE),
            ('rodoviaria tiete', self.RODOVIARIA_TIETE),
            ('estacao tiete', self.RODOVIARIA_TIETE),
            ('tiete', self.RODOVIARIA_TIETE),
        ]
        return OrderedDict(s_map)

    def find_synonym(self, term):
        """Find a synonym
        From the synonym map,
        find a match for the term
        """
        synonym_map = self.get_synonym_map()
        return synonym_map.get(term.query, None)

    def _transform(self, term):
        """Take a term and try
        to find a known synonym that is better
        understood by the later finders
        """
        synonym = self.find_synonym(term)
        if synonym is not None:
            return self.perform_transform(term, synonym)
        return term
