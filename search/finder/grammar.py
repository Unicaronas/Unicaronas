import re
import pickle
from collections import Counter
from unidecode import unidecode
from .base import BaseFinder
from .redis import RedisFinder


def words(text):
    return re.findall(r'\w+', unidecode(text.lower()))


def get_words():
    return Counter(words(open('search/finder/data/big.txt').read()))


def pickle_words():
    with open('search/finder/data/big.pkl', 'wb') as f:
        pickle.dump(get_words(), f, pickle.HIGHEST_PROTOCOL)


def unpickle_words():
    with open('search/finder/data/big.pkl', 'rb') as f:
        WORDS = pickle.load(f)
    return WORDS


IGNORED_WORDS = set(words(open('search/finder/data/ignored.txt').read())) | set([''])


class GrammarCorrectorFinder(BaseFinder):
    """
    Given a search term, perform grammar correction on it

    Inspired by Peter Norvig's simple spell corrector
    """

    def __init__(self, WORDS=unpickle_words(), IGNORED_WORDS=IGNORED_WORDS):
        self.WORDS = WORDS
        self.IGNORED_WORDS = IGNORED_WORDS
        self.N = sum(self.WORDS.values())

    def P(self, word):
        """Probability of `word` to appear on the corpus"""
        return self.WORDS[word] / self.N

    def candidates(self, word):
        """Generates possible spelling corrections for `word`"""
        return (self.known([word]) or self.known(self.edits1(word)) or self.known(self.edits2(word)) or [word])

    def known(self, words):
        """The subset of `words` that appear in the dictionary of WORDS."""
        return set(w for w in words if w in self.WORDS)

    def edits1(self, word):
        """All edits that are one edit away from `word`."""
        letters = 'abcdefghijklmnopqrstuvwxyz'
        splits = [(word[:i], word[i:]) for i in range(len(word) + 1)]
        deletes = [L + R[1:] for L, R in splits if R]
        transposes = [L + R[1] + R[0] + R[2:] for L, R in splits if len(R) > 1]
        replaces = [L + c + R[1:] for L, R in splits if R for c in letters]
        inserts = [L + c + R for L, R in splits for c in letters]
        return set(deletes + transposes + replaces + inserts)

    def edits2(self, word):
        """All edits that are two edits away from `word`."""
        return (e2 for e1 in self.edits1(word) for e2 in self.edits1(e1))

    def correction(self, word):
        """Most probable spelling correction for word."""
        # Only correct words
        return max(self.candidates(word), key=self.P)

    def recurse_correction(self, sentence, splits):
        """
        Recursively split the sentence into smaller sections until a clean word is found.
        correct it and then join it all back
        """
        if not splits:
            return self.correction(sentence) if sentence not in IGNORED_WORDS else sentence
        split = splits[0]
        return split.join([self.recurse_correction(sub_sentence, splits[1:]) for sub_sentence in sentence.split(split)])

    def correct_sentence(self, sentence):
        """
        Receives a (hopefully) prepared term sentence and apply correction to it
        """
        splits = {c for c in sentence if not c.isalnum()}
        return self.recurse_correction(sentence, list(splits))

    def _transform(self, term):
        """Take a term and try
        to perform word corrections on it
        and find a known synonym that is better
        understood by the later finders

        Since it takes a long time to correct each sentence, cache
        corrected results for some time.
        """
        # Use redis as cache
        cache = RedisFinder()

        request = term.request
        setattr(term, '_request', None)

        # Get the cached results if available
        cached_result = cache.get_key(cache.encode(term))
        if cached_result is not None:
            corrected_term = cached_result
        else:
            # If the corrected term is not cached, process it normally
            corrected_term = self.correct_sentence(term.query)
            # and then cache it
            cache.set_key(cache.encode(term), corrected_term)
        setattr(term, '_request', request)
        return self.perform_transform(term, corrected_term)
