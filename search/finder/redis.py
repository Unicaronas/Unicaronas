import pickle
from django.conf import settings
import redis
from .base import BaseCacheFinder


class RedisFinder(BaseCacheFinder):

    def __init__(self, url=None, timeout=604800, *args, **kwargs):
        self.url = settings.REDIS_URL or url
        super().__init__(*args, **kwargs)
        self.timeout = timeout

    def config_cache_engine(self):
        self._cache_engine = redis.StrictRedis.from_url(self.url)

    def extend_key(self, key):
        self.cache_engine.expire(key, self.timeout)

    def encode(self, value):
        return pickle.dumps(value)

    def decode(self, raw):
        if raw is None:
            return None
        return pickle.loads(raw)
