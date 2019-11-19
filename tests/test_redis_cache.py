import unittest
from unittest.mock import Mock

from tests import CacheTestCase
from cache_alchemy import redis_cache, method_redis_cache, property_redis_cache
import time


class RedisCacheTestCase(CacheTestCase):
    def test_cache_function(self):
        call_mock = Mock()

        @redis_cache
        def add(a: int, b: int = 2) -> int:
            call_mock()
            return a + b

        self.assertEqual(add(1), 3)
        self.assertEqual(1, call_mock.call_count)
        self.assertEqual(1, add.cache.misses)
        self.assertEqual(0, add.cache.hits)
        self.assertEqual(add(a=1), 3)
        self.assertEqual(2, add.cache.misses)
        self.assertEqual(0, add.cache.hits)
        self.assertEqual(2, call_mock.call_count)
        self.assertEqual(add(a=2), 4)
        self.assertEqual(3, call_mock.call_count)
        self.assertEqual(3, add.cache.misses)
        self.assertEqual(0, add.cache.hits)
        add.cache_clear()
        self.assertEqual(4, add(a=2))
        self.assertEqual(4, call_mock.call_count)

    def test_strict_cache_function(self):
        call_mock = Mock()

        @redis_cache(strict=True)
        def add(a: int, b: int = 2) -> int:
            call_mock()
            return a + b

        self.assertEqual(add(1), 3)
        self.assertEqual(1, call_mock.call_count)
        self.assertEqual(1, add.cache.misses)
        self.assertEqual(0, add.cache.hits)
        self.assertEqual(add(a=1), 3)
        self.assertEqual(1, add.cache.misses)
        self.assertEqual(1, add.cache.hits)
        self.assertEqual(1, call_mock.call_count)
        self.assertEqual(add(a=2), 4)
        self.assertEqual(2, call_mock.call_count)
        self.assertEqual(add.cache.misses, 2)
        self.assertEqual(add.cache.hits, 1)
        add.cache_clear()
        self.assertEqual(add(a=2), 4)
        self.assertEqual(3, call_mock.call_count)

    def test_cache_method(self):
        call_mock = Mock()

        class Tmp:
            @method_redis_cache
            def add(self, a: int, b: int = 2) -> int:
                call_mock()
                return a + b

        self.assertEqual(Tmp().add(1), 3)
        self.assertEqual(call_mock.call_count, 1)
        self.assertEqual(Tmp().add(1), 3)
        self.assertEqual(call_mock.call_count, 1)
        self.assertEqual(Tmp().add(2), 4)
        self.assertEqual(call_mock.call_count, 2)

    def test_cache_class_method(self):
        call_mock = Mock()

        class Tmp:
            @classmethod
            @method_redis_cache
            def add(cls, a: int, b: int = 2) -> int:
                call_mock()
                return a + b

        self.assertEqual(Tmp.add(1), 3)
        self.assertEqual(call_mock.call_count, 1)
        self.assertEqual(Tmp.add(1), 3)
        self.assertEqual(call_mock.call_count, 1)
        self.assertEqual(Tmp.add(2), 4)
        self.assertEqual(call_mock.call_count, 2)

    def test_cache_static_method(self):
        call_mock = Mock()

        class Tmp:
            @staticmethod
            @redis_cache
            def add(a: int, b: int = 2) -> int:
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
            @property_redis_cache
            def name(self) -> str:
                call_mock()
                return name

        self.assertEqual(Tmp().name, name)
        self.assertEqual(call_mock.call_count, 1)
        self.assertEqual(Tmp().name, name)
        self.assertEqual(call_mock.call_count, 1)

    def test_cache_clear(self):
        call_mock = Mock()

        @redis_cache
        def add(a: int, b: int = 2) -> int:
            call_mock()
            return a + b

        self.assertEqual(add(1), 3)
        self.assertEqual(call_mock.call_count, 1)
        add.cache_clear()
        self.assertEqual(add(a=1), 3)
        self.assertEqual(call_mock.call_count, 2)

    def test_redis_cache_limit(self):
        call_mock = Mock()

        @redis_cache(limit=1)
        def add(a: int, b: int = 2) -> int:
            call_mock()
            return a + b

        self.assertEqual(add(1), 3)
        self.assertEqual(call_mock.call_count, 1)
        self.assertEqual(add(a=2), 4)
        self.assertEqual(call_mock.call_count, 2)
        self.assertEqual(add(1), 3)
        self.assertEqual(call_mock.call_count, 3)

    def test_redis_cache_expire(self):
        call_mock = Mock()

        @redis_cache(expire=1)
        def add(a: int, b: int = 2) -> int:
            call_mock()
            return a + b

        self.assertEqual(add(1), 3)
        self.assertEqual(call_mock.call_count, 1)
        time.sleep(3)
        self.assertEqual(add(a=1), 3)
        self.assertEqual(call_mock.call_count, 2)

        unexpired_add_call_mock = Mock()

        @redis_cache(expire=-1)
        def unexpired_add(a: int, b: int = 2) -> int:
            unexpired_add_call_mock()
            return a + b

        self.assertEqual(unexpired_add(1), 3)
        self.assertEqual(unexpired_add_call_mock.call_count, 1)
        self.assertEqual(unexpired_add(1), 3)
        self.assertEqual(unexpired_add_call_mock.call_count, 1)


if __name__ == "__main__":
    unittest.main()
