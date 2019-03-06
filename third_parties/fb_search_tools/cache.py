import pickle
import redis

from django.conf import settings


class BaseCache(object):
    def __init__(self, timeout=3600, *args, **kwargs):
        self.timeout = timeout
        self.config_cache_engine()

    def config_cache_engine(self):
        raise NotImplementedError('implement cache')

    @property
    def cache_engine(self):
        return self._cache_engine

    def extend_key(self, key):
        pass

    def encode(self, value):
        return value

    def decode(self, raw):
        return raw

    def get_key(self, key, extend=True):
        """Gets a key from the cache. None if it does not exist"""
        value = self.decode(self.cache_engine.get(self.encode(key)))
        if value is not None and extend:
            # extend key
            self.extend_key(self.encode(key))
        return value

    def set_key(self, key, value):
        """Sets a key and a value, and adds the key to the index"""
        self.cache_engine.set(self.encode(key), self.encode(value), self.timeout)


class RedisCache(BaseCache):

    def __init__(self, url=None, timeout=86400, *args, **kwargs):
        self.url = settings.REDIS_URL or url
        super().__init__(timeout)

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
