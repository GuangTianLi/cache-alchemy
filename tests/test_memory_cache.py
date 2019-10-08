import unittest
from unittest.mock import Mock

from cache_alchemy import memory_cache, DefaultConfig
from cache_alchemy.lru_dict import LRUDict
from tests import CacheTestCase


class MemoryCacheTestCase(CacheTestCase):
    def test_expire_and_limit(self):
        tmp = lambda: ...
        with self.assertRaises(TypeError):
            memory_cache(limit=-2)(tmp)
        with self.assertRaises(TypeError):
            memory_cache(expire=-2)(tmp)

        self.assertEqual(tmp, memory_cache(expire=0)(tmp))
        self.assertEqual(tmp, memory_cache(limit=0)(tmp))

        cached_tmp = memory_cache(limit=-1)(tmp)
        self.assertIsInstance(cached_tmp.cache.cache_pool, dict)
        self.assertNotIsInstance(cached_tmp.cache.cache_pool, LRUDict)

    def test_distributed_memory_cache(self):
        call_mock = Mock()
        result = object()

        @memory_cache
        def add(a: int, b: int = 2) -> result:
            call_mock()
            return result

        self.assertEqual(result, add(1))
        self.assertEqual(call_mock.call_count, 1)
        self.assertEqual(add(1), result)
        self.assertEqual(call_mock.call_count, 1)
        self.assertEqual(add(2), result)
        self.assertEqual(call_mock.call_count, 2)

        add.cache_clear()
        self.assertEqual(add(2), result)
        self.assertEqual(call_mock.call_count, 3)

    def test_memory_cache(self):
        class TestMemoryCacheConfig(DefaultConfig):
            CACHE_ALCHEMY_MEMORY_BACKEND = "cache_alchemy.backends.memory.MemoryCache"

        config = TestMemoryCacheConfig()
        call_mock = Mock()
        result = object()

        @memory_cache
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
        add.cache_clear()
        self.assertEqual(add(1), result)
        self.assertEqual(call_mock.call_count, 3)


if __name__ == "__main__":
    unittest.main()
