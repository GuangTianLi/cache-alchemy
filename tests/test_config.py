import unittest

from cache_alchemy import DefaultConfig


class ConfigTestCase(unittest.TestCase):
    def test_get_current_config(self):
        with self.assertRaises(RuntimeError):
            DefaultConfig.get_current_config()

        class CacheConfig(DefaultConfig):
            ...

        cache_config = CacheConfig()
        self.assertEqual(cache_config, DefaultConfig.get_current_config())


if __name__ == "__main__":
    unittest.main()
