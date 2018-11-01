from collections import OrderedDict
from .base import BaseFinder


class SynonymFinder(BaseFinder):
    """
    Given a search term, look for synonyms

    Only transforms the input into a known
    synonym
    """

    def get_synonym_map(self):
        """Get a map of synonyms
        Used on autocorrected words to find the result
        """
        POSTO_IPIRANGA = 'posto ipiranga, unicamp'
        SP = 'sao paulo, sp'
        RODOVIARIA_TIETE = 'rodoviaria tiete, sao paulo'

        s_map = [
            # Map to posto ipiranga, Barão geraldo
            ('unicamp', POSTO_IPIRANGA),
            ('unichamps', POSTO_IPIRANGA),
            ('universidade estadual de campinas', POSTO_IPIRANGA),
            ('unicamp, campinas', POSTO_IPIRANGA),

            ('posto ipiranga, unicamp', POSTO_IPIRANGA),
            ('posto ipiranga unicamp', POSTO_IPIRANGA),
            ('posto ipiranga', POSTO_IPIRANGA),
            ('posto da 1', POSTO_IPIRANGA),
            ('posto', POSTO_IPIRANGA),

            ('barao geraldo', POSTO_IPIRANGA),
            ('barao', POSTO_IPIRANGA),
            ('bg', POSTO_IPIRANGA),

            # Map to generic São Paulo, SP
            ('sao paulo, sao paulo', SP),
            ('sao paulo sao paulo', SP),
            ('sao paulo, sp', SP),
            ('sao paulo sp', SP),
            ('sao paulo', SP),
            ('sp', SP),
            ('sampa', SP),

            # Map to rodoviária tietê
            ('rodoviaria tiete, sao paulo', RODOVIARIA_TIETE),
            ('rodoviaria tiete sao paulo', RODOVIARIA_TIETE),
            ('rodoviaria tiete, sp', RODOVIARIA_TIETE),
            ('rodoviaria tiete sp', RODOVIARIA_TIETE),
            ('rodoviaria tiete', RODOVIARIA_TIETE),
            ('estacao tiete', RODOVIARIA_TIETE),
            ('tiete', RODOVIARIA_TIETE),
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
