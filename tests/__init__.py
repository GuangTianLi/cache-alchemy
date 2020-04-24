import unittest

from fakeredis import FakeStrictRedis

from cache_alchemy.config import DefaultConfig


class TestCacheConfig(DefaultConfig):
    ...


def get_config():
    config = TestCacheConfig()
    config.cache_redis_client = FakeStrictRedis.from_url(config.CACHE_ALCHEMY_REDIS_URL)
    return config


class CacheTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.config = get_config()
        self.config.cache_redis_client.flushdb()
