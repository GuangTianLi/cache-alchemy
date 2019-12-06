=====
Usage
=====

.. warning:: The cache decorator must be used after config initialized.

.. warning:: The cache_redis_client must be assigned after config initialized if you want to use distributed cache.

To use Cache Alchemy in a project.

.. code-block:: python

    from cache_alchemy import memory_cache, redis_cache
    from cache_alchemy.config import DefaultConfig
    from redis import StrictRedis

    config = DefaultConfig()
    config.cache_redis_client = StrictRedis.from_url(config.CACHE_ALCHEMY_REDIS_URL, decode_responses=True)

    @memory_cache
    def add(i: complex, j: complex) -> complex:
        return i + j

    @redis_cache
    def add(i: int, j: int) -> int:
        return i + j

    class Foo:
        x = 2

        @classmethod
        @method_redis_cache
        def add(cls, y: int) -> int:
            return cls.x + b

        @method_redis_cache
        def pow(self, y: int) -> int:
            return pow(self.x, y)

        @property
        @property_redis_cache
        def name(self) -> int:
            return self.x

Configuration
==============================================

You can define your custom config by inherit from :any:`DefaultConfig` which defined
a list of configuration available in Cache Alchemy and their default values.

.. note:: DefaultConfig is defined by `configalchemy` - https://configalchemy.readthedocs.io

General Memory Cache
==========================

Cache Alchemy use distributed backend as default backend to cache function return value.

By setting ``CACHE_ALCHEMY_MEMORY_BACKEND`` to ``cache_alchemy.backends.memory.MemoryCache`` can enable general memory cache backend.

.. code-block:: python

    from cache_alchemy import memory_cache, redis_cache
    from cache_alchemy.config import DefaultConfig

    class CacheConfig(DefaultConfig):
        CACHE_ALCHEMY_MEMORY_BACKEND = "cache_alchemy.backends.memory.MemoryCache"

    config = CacheConfig()

    @memory_cache
    def add(i: complex, j: complex) -> complex:
        return i + j
