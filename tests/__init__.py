import unittest

from redis import Redis

from cache_alchemy.config import DefaultConfig


class TestRedisCacheConfig(DefaultConfig):
    ...


class CacheTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.config = TestRedisCacheConfig()
        self.config.client = Redis.from_url(self.config.CACHE_ALCHEMY_REDIS_URL)
        self.config.client.flushdb()
