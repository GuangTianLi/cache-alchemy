import unittest
from unittest.mock import Mock

from cache_alchemy import pickle_cache, method_pickle_cache, property_pickle_cache
from tests import CacheTestCase


class TestObject:
    def __init__(self, name: str):
        self.name = name

    def __eq__(self, other):
        return self.name == other.name


return_object = TestObject(name="world")


class PickleCacheTestCase(CacheTestCase):
    def test_cache_function(self):
        call_mock = Mock()

        @pickle_cache
        def hello(name: str) -> TestObject:
            call_mock()
            return return_object

        self.assertEqual(0, hello.cache_clear())
        self.assertEqual(hello("test"), return_object)
        self.assertEqual(1, call_mock.call_count)
        self.assertEqual(1, hello.cache.misses)
        self.assertEqual(0, hello.cache.hits)
        self.assertEqual(hello(name="test"), return_object)
        self.assertEqual(2, hello.cache.misses)
        self.assertEqual(0, hello.cache.hits)
        self.assertEqual(2, call_mock.call_count)
        self.assertEqual(hello(name="test"), return_object)
        self.assertEqual(2, call_mock.call_count)
        self.assertEqual(2, hello.cache.misses)
        self.assertEqual(1, hello.cache.hits)
        self.assertEqual(2, hello.cache_clear())

    def test_cache_method(self):
        call_mock = Mock()

        class Tmp:
            @method_pickle_cache
            def hello(self, name: str) -> TestObject:
                call_mock()
                return return_object

        self.assertEqual(Tmp().hello("test"), return_object)
        self.assertEqual(call_mock.call_count, 1)
        self.assertEqual(Tmp().hello("test"), return_object)
        self.assertEqual(call_mock.call_count, 1)
        self.assertEqual(Tmp().hello("world"), return_object)
        self.assertEqual(call_mock.call_count, 2)

    def test_cache_class_method(self):
        call_mock = Mock()

        class Tmp:
            @classmethod
            @method_pickle_cache
            def hello(self, name: str) -> TestObject:
                call_mock()
                return return_object

        self.assertEqual(Tmp.hello("test"), return_object)
        self.assertEqual(call_mock.call_count, 1)
        self.assertEqual(Tmp.hello("test"), return_object)
        self.assertEqual(call_mock.call_count, 1)
        self.assertEqual(Tmp.hello("world"), return_object)
        self.assertEqual(call_mock.call_count, 2)

    def test_cache_property(self):
        call_mock = Mock()

        class Tmp:
            @property
            @property_pickle_cache
            def name(self) -> TestObject:
                call_mock()
                return return_object

        self.assertEqual(Tmp().name, return_object)
        self.assertEqual(call_mock.call_count, 1)
        self.assertEqual(Tmp().name, return_object)
        self.assertEqual(call_mock.call_count, 1)


if __name__ == "__main__":
    unittest.main()
