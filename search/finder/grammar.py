from .base import BaseFinder


class GrammarCorrectorFinder(BaseFinder):
    """
    Given a search term, perform grammar correction on it

    Only transforms the input into a known
    synonym
    """

    def get_word_dictionary(self):
        return []

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
        # perform grammar correction
        corrected_words = [self.levenshtein_clean(word) for word in term.query.split()]
        corrected_term = ' '.join(corrected_words)
        return self.perform_transform(term, corrected_term)
