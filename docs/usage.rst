=====
Usage
=====

.. warning:: The cache decorator must be used after config initialized.

.. warning:: The cache_redis_client must be assigned after config initialized if you want to use distributed cache and set decode_responses to False.

To use Cache Alchemy in a project.

.. code-block:: python

    from cache_alchemy import memory_cache, json_cache, method_json_cache, property_json_cache
    from cache_alchemy.config import DefaultConfig
    from redis import Redis

    config = DefaultConfig()
    config.cache_redis_client = Redis.from_url(config.CACHE_ALCHEMY_REDIS_URL)

    @memory_cache()
    def add(i: complex, j: complex) -> complex:
        return i + j

    @json_cache()
    def add(i: int, j: int) -> int:
        return i + j

    class Foo:
        x = 2

        @classmethod
        @method_json_cache()
        def add(cls, y: int) -> int:
            return cls.x + b

        @method_json_cache()
        def pow(self, y: int) -> int:
            return pow(self.x, y)

        @property
        @property_json_cache()
        def name(self) -> int:
            return self.x

    # Using decorated function to clear cache
    add.cache_clear()


Json Cache
==============================================

.. note:: Json related cache only support function which return the pure `JSON serializable object <https://www.json.org/>`_. Otherwise there is a different between return value and cached value which will cause some unexpected behavior. If you want to cache python object e.g dataclass, see :ref:`pickle-cache`.


.. _pickle-cache:

Pickle Cache
========================

Pickle cache use `package - pickle <https://docs.python.org/3.7/library/pickle.html>`_ to serializing and de-serializing a Python object structure
which can handle and cache custom classes e.g: dataclass.

.. code-block:: python

    import dataclasses

    from redis import Redis

    from cache_alchemy import pickle_cache
    from cache_alchemy.config import DefaultConfig


    @dataclasses.dataclass
    class User:
        name: str


    config = DefaultConfig()
    config.cache_redis_client = Redis.from_url(config.CACHE_ALCHEMY_REDIS_URL)


    @pickle_cache()
    def add(i: complex, j: complex) -> complex:
        return i + j


    @pickle_cache()
    def access_user(name: str) -> User:
        return User(name=name)

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

    from cache_alchemy import memory_cache
    from cache_alchemy.config import DefaultConfig

    class CacheConfig(DefaultConfig):
        CACHE_ALCHEMY_MEMORY_BACKEND = "cache_alchemy.backends.memory.MemoryCache"

    config = CacheConfig()

    @memory_cache()
    def add(i: complex, j: complex) -> complex:
        return i + j

Define a cache dependency
===========================

Use cache dependency to declare dependency between two function.

.. code-block:: python

    @json_cache()
    def add(a, b):
        return a + b

    dependency = FunctionCacheDependency(add)

    @json_cache(dependency=[dependency])
    def add_and_double(a, b):
        return add(a, b) * 2

When cache of add has been cleared, add_and_double will clear cascade.
