import unittest
from unittest.mock import Mock

from tests import CacheTestCase
from cache_alchemy import json_cache
from cache_alchemy.dependency import FunctionCacheDependency


class DependencyTestCase(CacheTestCase):
    def test_function_dependency(self):
        call_mock = Mock()

        @json_cache
        def add(a, b):
            return a + b

        dependency = FunctionCacheDependency(add)

        @json_cache(dependency=[dependency])
        def add_and_double(a, b):
            call_mock()
            return add(a, b) * 2

        self.assertEqual(4, add_and_double(1, 1))
        self.assertEqual(1, call_mock.call_count)
        add.cache_clear()
        self.assertEqual(4, add_and_double(1, 1))
        self.assertEqual(2, call_mock.call_count)


if __name__ == "__main__":
    unittest.main()
