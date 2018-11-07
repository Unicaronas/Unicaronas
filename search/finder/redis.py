import pickle
from django.conf import settings
import redis
from .base import BaseCacheFinder


# Global redis connection that is kept open forever
global_redis = None


class RedisFinder(BaseCacheFinder):

    def __init__(self, url=None, timeout=604800, *args, **kwargs):
        self.url = settings.REDIS_URL or url
        super().__init__(*args, **kwargs)
        self.timeout = timeout

    def config_cache_engine(self):
        global global_redis
        if global_redis is None:
            # Only open one connection per worker/server
            kwargs = {
                'max_connections': 10,
                'timeout': 5
            }
            pool = redis.BlockingConnectionPool.from_url(self.url, **kwargs)
            global_redis = redis.StrictRedis(connection_pool=pool)
        self._cache_engine = global_redis

    def extend_key(self, key):
        self.cache_engine.expire(key, self.timeout)

    def encode(self, value):
        return pickle.dumps(value)

    def decode(self, raw):
        if raw is None:
            return None
        return pickle.loads(raw)
