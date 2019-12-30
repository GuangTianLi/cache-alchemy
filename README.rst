===============
Cache Alchemy
===============

.. image:: https://img.shields.io/pypi/v/cache-alchemy.svg
        :target: https://pypi.python.org/pypi/cache-alchemy

.. image:: https://img.shields.io/travis/GuangTianLi/cache-alchemy.svg
        :target: https://travis-ci.org/GuangTianLi/cache-alchemy

.. image:: https://readthedocs.org/projects/cache-alchemy/badge/?version=latest
        :target: https://cache-alchemy.readthedocs.io/en/latest/?badge=latest
        :alt: Documentation Status

.. image:: https://img.shields.io/pypi/pyversions/cache-alchemy.svg
        :target: https://pypi.org/project/cache-alchemy/

.. image:: https://codecov.io/gh/GuangTianLi/cache-alchemy/branch/master/graph/badge.svg
  :target: https://codecov.io/gh/GuangTianLi/cache-alchemy

.. image:: https://img.shields.io/badge/code%20style-black-000000.svg
  :target: https://github.com/psf/black



The Python Cache Toolkit.


* Free software: MIT license
* Documentation: https://cache-alchemy.readthedocs.io/en/latest/

Installation
----------------

.. code-block:: shell

    $ pipenv install cache-alchemy
    ✨🍰✨

Only **Python 3.6+** is supported.

Example
--------

.. code-block:: python

    from cache_alchemy import memory_cache, redis_cache
    from cache_alchemy.config import DefaultConfig
    from redis import Redis

    config = DefaultConfig()
    config.cache_redis_client = Redis.from_url(config.CACHE_ALCHEMY_REDIS_URL, decode_responses=True)

    @memory_cache
    def add(i: complex, j: complex) -> complex:
        return i + j

    @redis_cache
    def add(i: int, j: int) -> int:
        return i + j

Features
----------

- Cache ``Json Serializable`` function return value with Distributed Redis Cache
- Cache any function return value with Distributed Memory Cache
- LRU Dict support - behave like normal dict

TODO
-------
