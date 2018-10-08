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
        s_map = [
            # Map to posto ipiranga, Barão geraldo
            ('unicamp', 'posto ipiranga, unicamp'),
            ('unicamp', 'posto ipiranga unicamp'),
            ('universidade estadual de campinas', 'posto ipiranga, unicamp'),

            ('posto ipiranga, unicamp', 'posto ipiranga, unicamp'),
            ('posto ipiranga unicamp', 'posto ipiranga, unicamp'),
            ('posto ipiranga', 'posto ipiranga, unicamp'),
            ('posto da 1', 'posto ipiranga, unicamp'),
            ('posto', 'posto ipiranga, unicamp'),

            ('barao geraldo', 'posto ipiranga, unicamp'),
            ('barao', 'posto ipiranga, unicamp'),
            ('bg', 'posto ipiranga, unicamp'),

            # Map to generic São Paulo, SP
            ('sao paulo, sao paulo', 'sao paulo, sp'),
            ('sao paulo sao paulo', 'sao paulo, sp'),
            ('sao paulo, sp', 'sao paulo, sp'),
            ('sao paulo sp', 'sao paulo, sp'),
            ('sao paulo', 'sao paulo, sp'),
            ('sp', 'sao paulo, sp'),
            ('sampa', 'sao paulo, sp'),

            # Map to rodoviária tietê
            ('rodoviaria tiete, sao paulo', 'rodoviaria tiete, sao paulo'),
            ('rodoviaria tiete sao paulo', 'rodoviaria tiete, sao paulo'),
            ('rodoviaria tiete, sp', 'rodoviaria tiete, sao paulo'),
            ('rodoviaria tiete sp', 'rodoviaria tiete, sao paulo'),
            ('rodoviaria tiete', 'rodoviaria tiete, sao paulo'),
            ('estacao tiete', 'rodoviaria tiete, sao paulo'),
            ('tiete', 'rodoviaria tiete, sao paulo'),
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
