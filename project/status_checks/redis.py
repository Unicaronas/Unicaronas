import redis
from django.conf import settings
from django.utils.crypto import get_random_string
from watchman.decorators import check


@check
def _redis_check_connection():
    try:
        redis.StrictRedis.from_url(settings.REDIS_URL)
    except Exception as e:
        {'Connection': {'ok': False}}
    return {'Connection': {'ok': True}}


@check
def _redis_check_rw():
    try:
        s = get_random_string()
        r = redis.StrictRedis.from_url(settings.REDIS_URL)
        r.set('watchman_check', s, 30)
        v = r.get('watchman_check').decode()
        if v != s:
            return {'RW': {'ok': False}}
    except Exception as e:
        return {'RW': {'ok': False}}
    return {'RW': {'ok': True}}


def redis_check():
    return {'redis': [_redis_check_connection(), _redis_check_rw()]}
