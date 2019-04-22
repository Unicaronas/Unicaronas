from ..result.base import BaseResult
from ..term.base import BaseTerm
from ..term import Term


class BaseFinder(object):
    """Base cache finder
    Implements the basic interface used for
    searching for terms using cached items
    """

    def perform_transform(self, term, transformed):
        """Call term.transform to transform the term"""
        return term.transform(transformed)

    def _transform(self, term):
        return self.perform_transform(term, term.query)

    def transform(self, term):
        """
        Takes a term and transforms it into
        a more friendly format
        """
        assert isinstance(term, BaseTerm)
        transformation = self._transform(term)
        assert isinstance(transformation, BaseTerm)
        return transformation

    def _search(self, term):
        return None

    def search(self, term):
        """Search a term within the defined cache
        Returns a SearchResult if found and None if not
        """
        assert isinstance(term, BaseTerm)
        result = self._search(term)
        assert isinstance(result, (type(None), BaseResult))
        return result

    def _cache(self, result):
        return

    def cache(self, result):
        """Receives and caches a SearchResult"""
        assert isinstance(result, BaseResult)
        self._cache(result)

    def _hit(self, term):
        return

    def hit(self, term):
        """Registers a search hit"""
        assert isinstance(term, Term)
        self._hit(term)


class BaseCacheFinder(BaseFinder):
    """Base cache finder

    Indexes all cached keys in a special cached object

    loads this list into memory and then performs operations onto it,
    like levenshtein searches
    """

    index_key = 'base_cache_index'

    def __init__(self, timeout=600, *args, **kwargs):
        # Default timeout in seconds
        self.timeout = timeout
        super().__init__(*args, **kwargs)
        self.config_cache_engine()

    def config_cache_engine(self):
        raise NotImplementedError('Implement a configuration for the cache engine')

    @property
    def cache_engine(self):
        return self._cache_engine

    def encode(self, value):
        """
        Encode keys before adding them to the cache.
        Defaults to no encoding
        """
        return value

    def decode(self, raw):
        """
        Decode keys before getting them from the cache.
        Defaults to no decoding
        """
        return raw

    def extend_key(self, key):
        """Extends the timeout of a key"""
        raise NotImplementedError('Implement a way to extend the key lifetime')

    def set_index(self, index):
        """Sets the index as a new set"""
        assert isinstance(index, set)
        self.cache_engine.set(self.index_key, self.encode(index), self.timeout)

    def get_index(self):
        """Retrieves the index set of saved keys"""
        index = self.decode(self.cache_engine.get(self.index_key))
        if index is None:
            self.set_index(set())
            index = self.get_index()
        else:
            self.extend_key(self.index_key)
        return index

    def add_to_index(self, key):
        """Adds a new key to the index"""
        index = self.get_index()
        index.add(key)
        self.set_index(index)

    def remove_from_index(self, key):
        """Removes a key from the index"""
        index = self.get_index()
        try:
            index.remove(key)
        except KeyError:
            return
        self.set_index(index)

    def get_key(self, key):
        """Gets a key from the cache. None if it does not exist"""
        if key == self.index_key:
            # Prevent getting the index
            return None
        value = self.decode(self.cache_engine.get(key))
        if value is not None:
            # extend key
            self.extend_key(key)
        return value

    def set_key(self, key, value):
        """Sets a key and a value, and adds the key to the index"""
        if key == self.index_key:
            # Prevent setting the index
            return
        self.cache_engine.set(key, self.encode(value), self.timeout)
        self.add_to_index(key)

    def delete_key(self, key):
        """Removes a key from the index if it exists"""
        self.cache_engine.delete(key)

    def find_exact(self, term):
        """Fast searching of term in cache"""
        return self.get_key(term.query)

    def _search(self, term):
        """Search
        Searches the cache for a term or a permutation
        of it.
        """
        premature_results = self.find_exact(term)
        if premature_results is not None:
            return premature_results
        # Do magic with permutations
        return None

    def _cache(self, result):
        """Cache the result for future searches"""
        self.set_key(result.query, result)

    def _hit(self, term):
        """
        Assume that the term is present since
        the steps before also have the key,
        so only extend the key lifetime on hit
        """
        self.find_exact(term)
