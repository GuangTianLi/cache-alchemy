import unittest
from unittest.mock import Mock

from cache_alchemy import memory_cache, DefaultConfig
from tests import CacheTestCase


class MemoryCacheTestCase(CacheTestCase):
    def test_distributed_memory_cache(self):
        call_mock = Mock()
        result = object()

        @memory_cache()
        def add(a: int, b: int = 2) -> result:
            call_mock()
            return result

        self.assertEqual(add(1), result)
        self.assertEqual(call_mock.call_count, 1)
        self.assertEqual(add(1), result)
        self.assertEqual(call_mock.call_count, 1)
        self.assertEqual(add(2), result)
        self.assertEqual(call_mock.call_count, 2)

    def test_memory_cache(self):
        class TestMemoryCacheConfig(DefaultConfig):
            CACHE_ALCHEMY_MEMORY_BACKEND = "cache_alchemy.backends.memory.MemoryCache"

        config = TestMemoryCacheConfig()
        call_mock = Mock()
        result = object()

        @memory_cache()
        def add(a: int, b: int = 2) -> result:
            self.assertEqual(config, DefaultConfig.get_current_config())
            call_mock()
            return result

        self.assertEqual(add(1), result)
        self.assertEqual(call_mock.call_count, 1)
        self.assertEqual(add(1), result)
        self.assertEqual(call_mock.call_count, 1)
        self.assertEqual(add(2), result)
        self.assertEqual(call_mock.call_count, 2)


if __name__ == "__main__":
    unittest.main()
