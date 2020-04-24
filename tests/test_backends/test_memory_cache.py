import time
import unittest
from typing import Type
from unittest.mock import Mock

from configalchemy.utils import import_reference

from cache_alchemy import (
    memory_cache,
    DefaultConfig,
    method_memory_cache,
    property_memory_cache,
)
from cache_alchemy.backends.memory import MemoryCache
from cache_alchemy.backends.memory import all_cache_pool
from cache_alchemy.lru import LRUDict
from cache_alchemy.utils import UnsupportedError
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
        with self.assertRaises(UnsupportedError):
            cached_tmp.cache_clear(1)

    def test_cache_class_method(self):
        call_mock = Mock()

        class Tmp:
            @classmethod
            @method_memory_cache
            def add(cls, a: int, b: int = 2) -> int:
                call_mock()
                return a + b

        self.assertEqual(Tmp.add(1), 3)
        self.assertEqual(call_mock.call_count, 1)
        self.assertEqual(Tmp.add(1), 3)
        self.assertEqual(call_mock.call_count, 1)
        self.assertEqual(Tmp.add(2), 4)
        self.assertEqual(call_mock.call_count, 2)

    def test_cache_property(self):
        call_mock = Mock()
        name = "test"

        class Tmp:
            @property
            @property_memory_cache
            def name(self) -> str:
                call_mock()
                return name

        self.assertEqual(Tmp().name, name)
        self.assertEqual(call_mock.call_count, 1)
        self.assertEqual(Tmp().name, name)
        self.assertEqual(call_mock.call_count, 1)

    def test_distributed_memory_cache(self):
        call_mock = Mock()
        result = object()

        @memory_cache
        def add(a: int, b: int = 2) -> result:
            call_mock()
            return result

        self.assertEqual(0, add.cache_clear())
        self.assertEqual(result, add(1))
        self.assertEqual(call_mock.call_count, 1)
        self.assertEqual(add(1), result)
        self.assertEqual(call_mock.call_count, 1)
        self.assertEqual(add(a=1), result)
        self.assertEqual(call_mock.call_count, 2)
        self.assertEqual(add(2), result)
        self.assertEqual(call_mock.call_count, 3)

        self.assertEqual(3, add.cache_clear())
        self.assertEqual(add(2), result)
        self.assertEqual(call_mock.call_count, 4)

    def test_distributed_strict_memory_cache(self):
        call_mock = Mock()
        result = object()

        @memory_cache(strict=True)
        def add(a: int, b: int = 2) -> result:
            call_mock()
            return result

        self.assertEqual(result, add(1))
        self.assertEqual(call_mock.call_count, 1)
        self.assertEqual(add(1), result)
        self.assertEqual(call_mock.call_count, 1)
        self.assertEqual(add(a=1), result)
        self.assertEqual(call_mock.call_count, 1)
        self.assertEqual(add(2), result)
        self.assertEqual(call_mock.call_count, 2)

        add.cache_clear()
        self.assertEqual(add(1, b=2), result)
        self.assertEqual(call_mock.call_count, 3)

    def test_memory_cache(self):
        all_cache_pool.clear()

        class TestMemoryCacheConfig(DefaultConfig):
            CACHE_ALCHEMY_MEMORY_BACKEND = "cache_alchemy.backends.memory.MemoryCache"

        config = TestMemoryCacheConfig()
        call_mock = Mock()
        result = object()
        cache_backend: Type[MemoryCache] = import_reference(
            config.CACHE_ALCHEMY_MEMORY_BACKEND
        )

        self.assertEqual(set(), cache_backend.get_all_namespace())

        @memory_cache
        def add(a: int, b: int = 2) -> result:
            self.assertEqual(config, DefaultConfig.get_current_config())
            call_mock()
            return result

        self.assertIn(
            cache_backend.__name__, add.cache.make_key(args=(1,), kwargs={})[2]
        )
        self.assertEqual(0, len(cache_backend.get_all_namespace()))

        self.assertEqual(add(1), result)
        self.assertEqual(1, len(cache_backend.get_all_namespace()))
        self.assertEqual(call_mock.call_count, 1)
        self.assertEqual(add(a=1), result)
        self.assertEqual(call_mock.call_count, 2)
        self.assertEqual(add(2), result)
        self.assertEqual(call_mock.call_count, 3)
        self.assertEqual(3, add.cache_clear())
        self.assertEqual(add(1), result)
        self.assertEqual(call_mock.call_count, 4)
        self.assertEqual(1, cache_backend.flush_cache())

    def test_strict_memory_cache(self):
        class TestMemoryCacheConfig(DefaultConfig):
            CACHE_ALCHEMY_MEMORY_BACKEND = "cache_alchemy.backends.memory.MemoryCache"

        config = TestMemoryCacheConfig()
        call_mock = Mock()
        result = object()

        @memory_cache(strict=True)
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

    def test_cache_namespace_hash(self):
        from tests import resource_a, resource_b

        resource_a.memory_test()
        resource_b.memory_test()
        resource_a.memory_test()
        resource_b.memory_test()
        self.assertEqual(1, resource_a.memory_call_mock.call_count)
        self.assertEqual(1, resource_b.memory_call_mock.call_count)

    def test_cache_clear_with_pattern(self):
        class TestMemoryCacheConfig(DefaultConfig):
            CACHE_ALCHEMY_MEMORY_BACKEND = "cache_alchemy.backends.memory.MemoryCache"

        config = TestMemoryCacheConfig()
        call_mock = Mock()
        result = object()

        @memory_cache(strict=True)
        def add(a: int, b: int = 2) -> result:
            self.assertEqual(config, DefaultConfig.get_current_config())
            call_mock()
            return result

        add(1)
        self.assertEqual(1, call_mock.call_count)
        add(a=2)
        self.assertEqual(2, call_mock.call_count)
        self.assertEqual(1, add.cache_clear(a=1))
        add(2)
        self.assertEqual(2, call_mock.call_count)
        add(1)
        self.assertEqual(3, call_mock.call_count)

    def test_distributed_strict_memory_cache_clear_with_pattern(self):
        call_mock = Mock()
        result = object()

        @memory_cache(strict=True)
        def add(a: int, b: int = 2) -> result:
            call_mock()
            return result

        add(1)
        self.assertEqual(1, call_mock.call_count)
        add(a=2)
        self.assertEqual(2, call_mock.call_count)
        add.cache_clear(a=1)
        add(2)
        self.assertEqual(2, call_mock.call_count)
        add(1)
        self.assertEqual(3, call_mock.call_count)

    def test_memory_cache_expire(self):
        call_mock = Mock()

        @memory_cache(expire=1)
        def add(a: int, b: int = 2) -> int:
            call_mock()
            return a + b

        self.assertEqual(add(1), 3)
        self.assertEqual(call_mock.call_count, 1)
        time.sleep(3)
        self.assertEqual(add(1), 3)
        self.assertEqual(call_mock.call_count, 2)


if __name__ == "__main__":
    unittest.main()
