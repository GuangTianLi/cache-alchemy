===============
Cache Alchemy
===============

.. image:: https://img.shields.io/pypi/v/cache_alchemy.svg
        :target: https://pypi.python.org/pypi/cache_alchemy

.. image:: https://img.shields.io/travis/GuangTianLi/cache_alchemy.svg
        :target: https://travis-ci.org/GuangTianLi/cache_alchemy

.. image:: https://readthedocs.org/projects/cache_alchemy/badge/?version=latest
        :target: https://cache_alchemy.readthedocs.io/en/latest/?badge=latest
        :alt: Documentation Status

.. image:: https://img.shields.io/pypi/pyversions/cache_alchemy.svg
        :target: https://pypi.org/project/cache_alchemy/

.. image:: https://codecov.io/gh/GuangTianLi/cache_alchemy/branch/master/graph/badge.svg
  :target: https://codecov.io/gh/GuangTianLi/cache_alchemy

.. image:: https://img.shields.io/badge/code%20style-black-000000.svg
  :target: https://github.com/psf/black



The Python Cache Toolkit.


* Free software: MIT license
* Documentation: https://cache_alchemy.readthedocs.io/en/latest/

Installation
----------------

.. code-block:: shell

    $ pipenv install cache_alchemy
    ✨🍰✨

Only **Python 3.6+** is supported.

Example
--------

.. code-block:: python

    from cache_alchemy import memory_cache, redis_cache
    from cache_alchemy.config import DefaultConfig
    from redis import StrictRedis

    config = DefaultConfig()
    config.client = StrictRedis.from_url(config.CACHE_ALCHEMY_REDIS_URL)

    @memory_cache()
    def add(i: complex, j: complex) -> complex:
        return i + j

    @redis_cache()
    def add(i: int, j: int) -> int:
        return i + j

Features
----------

- Cache ``Json Serializable`` function return value with Distributed Redis Cache
- Cache any function return value with Distributed Memory Cache

TODO
-------
