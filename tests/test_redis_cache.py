import unittest
from unittest.mock import Mock

from tests import CacheTestCase
from cache_alchemy import redis_cache


class RedisCacheTestCase(CacheTestCase):
    def test_cache_function(self):
        call_mock = Mock()

        @redis_cache()
        def add(a: int, b: int = 2) -> int:
            call_mock()
            return a + b

        self.assertEqual(add(1), 3)
        self.assertEqual(call_mock.call_count, 1)
        self.assertEqual(1, add.cache.misses)
        self.assertEqual(0, add.cache.hits)
        self.assertEqual(add(a=1), 3)
        self.assertEqual(1, add.cache.misses)
        self.assertEqual(1, add.cache.hits)
        self.assertEqual(call_mock.call_count, 1)
        self.assertEqual(add(a=2), 4)
        self.assertEqual(call_mock.call_count, 2)
        self.assertEqual(2, add.cache.misses)
        self.assertEqual(1, add.cache.hits)

    def test_cache_method(self):
        call_mock = Mock()

        class Tmp:
            @redis_cache(is_method=True)
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
            @redis_cache(is_method=True)
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
            @redis_cache()
            def add(a: int, b: int = 2) -> int:
                call_mock()
                return a + b

        self.assertEqual(Tmp.add(1), 3)
        self.assertEqual(call_mock.call_count, 1)
        self.assertEqual(Tmp.add(1), 3)
        self.assertEqual(call_mock.call_count, 1)
        self.assertEqual(Tmp.add(2), 4)
        self.assertEqual(call_mock.call_count, 2)

    def test_cache_clear(self):
        call_mock = Mock()

        @redis_cache()
        def add(a: int, b: int = 2) -> int:
            call_mock()
            return a + b

        self.assertEqual(add(1), 3)
        self.assertEqual(call_mock.call_count, 1)
        add.cache_clear()
        self.assertEqual(add(a=1), 3)
        self.assertEqual(call_mock.call_count, 2)


if __name__ == "__main__":
    unittest.main()
