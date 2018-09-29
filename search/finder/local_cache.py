from django.core.cache import cache
from .base import BaseCacheFinder


class LocalCacheFinder(BaseCacheFinder):

    def config_cache_engine(self):
        self._cache_engine = cache

    def extend_key(self, key):
        try:
            self.cache_engine.touch(key, self.timeout)
        except NotImplementedError:
            pass
