from urlparse import urlparse
from redis import StrictRedis


class RedisAdapter(object):

    name = "redis"

    def get_value(self, key):
        return self._redis.hget(self._redis_key, key)

    def set_value(self, key, value):
        self._redis.hset(self._redis_key, key, value)

    def remove_key(self, key):
        self._redis.hdel(self._redis_key, key)

    def get_keys(self):
        return self._redis.hkeys(self._redis_key)

    def __init__(self, uri):
        """redis://localhost:6379/0?default"""
        _uri = urlparse(uri, scheme="redis")
        self._redis = StrictRedis(
            host=_uri.hostname,
            port=_uri.port or 6379,
            db=_uri.path.lstrip('/') or 0,
            password=_uri.password
        )
        self._redis_key = "keystore:{}".format(
            _uri.query.lower() or 'default'
        )
