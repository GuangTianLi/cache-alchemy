import time
import unittest
from typing import Type
from unittest.mock import Mock

from configalchemy.utils import import_reference

from cache_alchemy import json_cache, method_json_cache, property_json_cache
from cache_alchemy.backends.json import DistributedJsonCache
from cache_alchemy.utils import UnsupportedError
from tests import CacheTestCase


class JsonCacheTestCase(CacheTestCase):
    def test_cache_function(self):
        call_mock = Mock()

        @json_cache()
        def add(a: int, b: int = 2) -> int:
            call_mock()
            return a + b

        self.assertEqual(0, add.cache_clear())
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
        self.assertEqual(3, add.cache_clear())
        self.assertEqual(4, add(a=2))
        self.assertEqual(4, call_mock.call_count)

    def test_cache_namespace_hash(self):
        from tests import resource_a, resource_b

        resource_a.json_test()
        resource_b.json_test()
        resource_a.json_test()
        resource_b.json_test()
        self.assertEqual(1, resource_a.redis_call_mock.call_count)
        self.assertEqual(1, resource_b.redis_call_mock.call_count)

    def test_cache_clear(self):
        call_mock = Mock()

        @json_cache()
        def add(a: int, b: int = 2) -> int:
            call_mock()
            return a + b

        self.assertEqual(add(1), 3)
        self.assertEqual(call_mock.call_count, 1)
        add.cache_clear()
        self.assertEqual(add(a=1), 3)
        self.assertEqual(call_mock.call_count, 2)

        with self.assertRaises(UnsupportedError):
            add.cache_clear(a=1)

    def test_cache_set(self):
        self.config.cache_redis_client.flushdb()
        json_cache_backend: Type[DistributedJsonCache] = import_reference(
            self.config.CACHE_ALCHEMY_JSON_BACKEND
        )

        self.assertEqual(
            set(),
            json_cache_backend.get_all_namespace(
                self.config.CACHE_ALCHEMY_CACHE_KEY_PREFIX
            ),
        )

        @json_cache()
        def add(a: int, b: int = 2) -> int:
            return a + b

        @json_cache()
        def mul(a: int, b: int = 2) -> int:
            return a * b

        self.assertIn(
            json_cache_backend.__name__, add.cache.make_key(args=(1,), kwargs={})[2]
        )
        self.assertEqual(
            0,
            len(
                json_cache_backend.get_all_namespace(
                    self.config.CACHE_ALCHEMY_CACHE_KEY_PREFIX
                )
            ),
        )
        self.assertEqual(
            0,
            json_cache_backend.flush_cache(self.config.CACHE_ALCHEMY_CACHE_KEY_PREFIX),
        )
        add(1)
        self.assertEqual(
            1,
            len(
                json_cache_backend.get_all_namespace(
                    self.config.CACHE_ALCHEMY_CACHE_KEY_PREFIX
                )
            ),
        )
        self.assertEqual(
            1,
            json_cache_backend.flush_cache(self.config.CACHE_ALCHEMY_CACHE_KEY_PREFIX),
        )
        add(1)
        self.assertEqual(2, add.cache.misses)
        mul(1)
        self.assertEqual(
            2,
            len(
                json_cache_backend.get_all_namespace(
                    self.config.CACHE_ALCHEMY_CACHE_KEY_PREFIX
                )
            ),
        )
        self.assertEqual(
            2,
            json_cache_backend.flush_cache(self.config.CACHE_ALCHEMY_CACHE_KEY_PREFIX),
        )

    def test_cache_clear_with_pattern_and_int_parameter(self):
        call_mock = Mock()

        @json_cache(strict=True)
        def add(a: int, b: int = 2) -> int:
            call_mock()
            return a + b

        add(1)
        self.assertEqual(1, call_mock.call_count)
        add(a=2)
        self.assertEqual(2, call_mock.call_count)
        self.assertEqual(1, add.cache_clear(a=1))
        add(2)
        self.assertEqual(2, call_mock.call_count)
        add(1)
        self.assertEqual(3, call_mock.call_count)
        self.assertEqual(0, add.cache_clear(a=3))

    def test_cache_clear_with_pattern_and_str_parameter(self):
        call_mock = Mock()

        @json_cache(strict=True)
        def hello(name: str, status: str = "") -> str:
            call_mock()
            return ""

        hello(name="world", status="test")
        hello(name="world", status="prod")
        self.assertEqual(2, call_mock.call_count)
        self.assertEqual(1, hello.cache_clear(name="world", status="prod"))

    def test_strict_cache_function(self):
        call_mock = Mock()

        @json_cache(strict=True)
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
            @method_json_cache
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
            @method_json_cache()
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
            @json_cache()
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
            @property_json_cache()
            def name(self) -> str:
                call_mock()
                return name

        self.assertEqual(Tmp().name, name)
        self.assertEqual(call_mock.call_count, 1)
        self.assertEqual(Tmp().name, name)
        self.assertEqual(call_mock.call_count, 1)

    def test_json_cache_limit(self):
        call_mock = Mock()

        @json_cache(limit=1)
        def add(a: int, b: int = 2) -> int:
            call_mock()
            return a + b

        self.assertEqual(add(1), 3)
        self.assertEqual(call_mock.call_count, 1)
        self.assertEqual(add(a=2), 4)
        self.assertEqual(call_mock.call_count, 2)
        self.assertEqual(add(1), 3)
        self.assertEqual(call_mock.call_count, 3)

    def test_json_cache_expire(self):
        call_mock = Mock()

        @json_cache(expire=1)
        def add(a: int, b: int = 2) -> int:
            call_mock()
            return a + b

        self.assertEqual(add(1), 3)
        self.assertEqual(call_mock.call_count, 1)
        time.sleep(3)
        self.assertEqual(add(1), 3)
        self.assertEqual(call_mock.call_count, 2)

        unexpired_add_call_mock = Mock()

        @json_cache(expire=-1)
        def unexpired_add(a: int, b: int = 2) -> int:
            unexpired_add_call_mock()
            return a + b

        self.assertEqual(unexpired_add(1), 3)
        self.assertEqual(unexpired_add_call_mock.call_count, 1)
        self.assertEqual(unexpired_add(1), 3)
        self.assertEqual(unexpired_add_call_mock.call_count, 1)


if __name__ == "__main__":
    unittest.main()
