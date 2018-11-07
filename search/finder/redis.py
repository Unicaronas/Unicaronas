import pickle
from django.conf import settings
import redis
from .base import BaseCacheFinder


# Global redis pool that is kept open forever
global_redis_pool = None


class RedisFinder(BaseCacheFinder):

    def __init__(self, url=None, timeout=604800, *args, **kwargs):
        self.url = settings.REDIS_URL or url
        super().__init__(*args, **kwargs)
        self.timeout = timeout

    def config_cache_engine(self):
        if global_redis_pool is None:
            global global_redis_pool
            # Only open one connection per worker/server
            kwargs = {
                'max_connections': 10,
                'timeout': 5
            }
            global_redis_pool = redis.BlockingConnectionPool.from_url(self.url, **kwargs)
        self._cache_engine = redis.StrictRedis(connection_pool=global_redis_pool)

    def extend_key(self, key):
        self.cache_engine.expire(key, self.timeout)

    def encode(self, value):
        return pickle.dumps(value)

    def decode(self, raw):
        if raw is None:
            return None
        return pickle.loads(raw)
