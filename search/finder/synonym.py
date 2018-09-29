from .base import BaseFinder


class SynonymFinder(BaseFinder):
    """
    Given a search term, look for synonyms

    Only transforms the input into a known
    synonym
    """

    def get_word_dictionary(self):
        """Get a dictionay of common words
        for autocorrection
        """
        return []

    def get_synonym_map(self):
        """Get a map of synonyms
        Used on autocorrected words to find the result
        """
        return {}

    def find_synonym(self, term):
        """Find a synonym
        From the synonym map,
        find a match for the term
        """
        synonym_map = self.get_synonym_map()
        return synonym_map.get(term, None)

    def levenshtein_clean(self, word):
        """
        From a dictionary of words,
        try to find a word that is at most n
        permutations from `word` and take it
        """
        dictionary = self.get_word_dictionary()
        dictionary
        # Do magic here
        return word

    def _transform(self, term):
        """Take a term and try
        to perform word corrections on it
        and find a known synonym that is better
        understood by the later finders
        """
        # Try to find a match right away
        premature_results = self.find_synonym(term)
        if premature_results is not None:
            return self.perform_transform(term, premature_results)

        # If no synonym was found right away,
        # perform grammar correction
        corrected_words = [self.levenshtein_clean(word) for word in term.query.split()]
        corrected_term = ' '.join(corrected_words)
        results = self.find_synonym(corrected_term)
        if results is not None:
            return self.perform_transform(term, results)
        return term
