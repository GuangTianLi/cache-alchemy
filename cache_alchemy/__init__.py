"""
Caching framework.
"""
__version__ = "0.4.5"

from functools import wraps
from importlib import import_module
from types import FunctionType
from typing import Callable, List, Optional, cast, Type, TypeVar

from .backends.base import BaseCache, CacheFunctionType
from .config import DefaultConfig
from .dependency import CacheDependency
from .lru import LRUDict
from .utils import UnsupportedError

BackendCls = TypeVar("BackendCls", bound=BaseCache)


def _create_cache(
    *,
    backend_cls: Type[BackendCls],
    cached_function: FunctionType,
    expire: Optional[int],
    limit: Optional[int],
    is_method: bool = False,
    strict: bool = False,
    cache_key_prefix: str = "",
    **kwargs,
) -> BackendCls:

    if not isinstance(limit, int) or limit < -1:
        raise TypeError("Expected limit to larger equal than -1")
    if not isinstance(expire, int) or expire < -1:
        raise TypeError("Expected expire to larger equal than -1")

    return backend_cls(  # type: ignore
        cached_function=cached_function,
        expire=expire,
        limit=limit,
        is_method=is_method,
        strict=strict,
        cache_key_prefix=cache_key_prefix,
        **kwargs,
    )


CacheDecoratorType = Callable[[FunctionType], CacheFunctionType]


def cache(
    limit: Optional[int],
    expire: Optional[int],
    is_method: bool,
    strict: bool,
    backend: str,
    dependency: List[CacheDependency],
    cache_key_prefix: str = "",
    **kwargs,
) -> CacheDecoratorType:
    """The base function to creat a cache object like this::

        @cache(
            limit=1000,
            expire=60,
            is_method=False,
            strict=True,
            backend="cache_alchemy.backends.memory.MemoryCache",
            dependency=[],
        )
        def f(x, y):
            pass

        # To clear cache
        f.cache_clear()

    :param int expire: expire time with an integer value used as seconds.
    :param bool is_method: If *True*, the first argument will be ignored in generate cache key.
    :param bool strict: If *False*, make a cache key in a way that is flat as possible rather than
                        as a nested and strict structure that would support partially cache clear.
                        it means that f(x=1, y=2) will now be treated as a distinct call from
                        f(y=2, x=1) which will be cached separately.
    """
    config = DefaultConfig.get_current_config()
    module_path, class_name = backend.rsplit(".", 1)
    backend_cls = getattr(import_module(module_path), class_name)

    if limit is None:
        limit = config.CACHE_ALCHEMY_DEFAULT_LIMIT
    if expire is None:
        expire = config.CACHE_ALCHEMY_DEFAULT_EXPIRE
    cache_key_prefix = cache_key_prefix or config.CACHE_ALCHEMY_CACHE_KEY_PREFIX

    def decorating_function(func: CacheFunctionType) -> CacheFunctionType:
        if limit == 0 or expire == 0:
            return func

        cache = _create_cache(
            backend_cls=backend_cls,
            expire=expire,
            cached_function=cast(FunctionType, func),
            limit=limit,
            is_method=is_method,
            strict=strict,
            cache_key_prefix=cache_key_prefix,
            **kwargs,
        )

        @wraps(func)
        def wrapper(*args, **kwargs):
            return cache(*args, **kwargs)

        def cache_clear(*args, **kwargs) -> int:
            """Clear the cache and cache statistics"""
            if not strict and (args or kwargs):
                raise UnsupportedError("fast hash not support pattern delete")

            return sum(
                [
                    cache.cache_clear(args, kwargs),
                    CacheDependency.dependent_cache_clear(cache, args, kwargs),
                ]
            )

        for item in dependency:
            item.cache_objects.add(cache)
            CacheDependency.register_dependency(item)

        wrapper.cache = cache  # type: ignore
        wrapper.cache_clear = cache_clear  # type: ignore
        return wrapper

    if callable(limit):
        user_function, limit = limit, config.CACHE_ALCHEMY_DEFAULT_LIMIT
        return decorating_function(user_function)
    return decorating_function


def json_cache(
    limit: Optional[int] = None,
    *,
    expire: Optional[int] = None,
    is_method: bool = False,
    strict: bool = False,
    dependency: Optional[List[CacheDependency]] = None,
    cache_key_prefix: str = "",
    **kwargs,
) -> CacheDecoratorType:
    return cache(
        limit=limit,
        expire=expire,
        is_method=is_method,
        strict=strict,
        backend=DefaultConfig.get_current_config().CACHE_ALCHEMY_JSON_BACKEND,
        dependency=dependency or [],
        cache_key_prefix=cache_key_prefix,
        **kwargs,
    )


def method_json_cache(
    limit: Optional[int] = None,
    *,
    expire: Optional[int] = None,
    strict: bool = False,
    dependency: Optional[List[CacheDependency]] = None,
    cache_key_prefix: str = "",
    **kwargs,
) -> CacheDecoratorType:
    return cache(
        limit=limit,
        expire=expire,
        is_method=True,
        strict=strict,
        backend=DefaultConfig.get_current_config().CACHE_ALCHEMY_JSON_BACKEND,
        dependency=dependency or [],
        cache_key_prefix=cache_key_prefix,
        **kwargs,
    )


def property_json_cache(
    limit: Optional[int] = None,
    *,
    expire: Optional[int] = None,
    strict: bool = False,
    dependency: Optional[List[CacheDependency]] = None,
    cache_key_prefix: str = "",
    **kwargs,
) -> CacheDecoratorType:
    return cache(
        limit=limit,
        expire=expire,
        is_method=True,
        strict=strict,
        backend=DefaultConfig.get_current_config().CACHE_ALCHEMY_JSON_BACKEND,
        dependency=dependency or [],
        cache_key_prefix=cache_key_prefix,
        **kwargs,
    )


def memory_cache(
    limit: Optional[int] = None,
    *,
    expire: Optional[int] = None,
    is_method: bool = False,
    strict: bool = False,
    dependency: Optional[List[CacheDependency]] = None,
    cache_key_prefix: str = "",
    **kwargs,
) -> CacheDecoratorType:
    return cache(
        limit=limit,
        expire=expire,
        is_method=is_method,
        strict=strict,
        backend=DefaultConfig.get_current_config().CACHE_ALCHEMY_MEMORY_BACKEND,
        dependency=dependency or [],
        cache_key_prefix=cache_key_prefix,
        **kwargs,
    )


def method_memory_cache(
    limit: Optional[int] = None,
    *,
    expire: Optional[int] = None,
    strict: bool = False,
    dependency: Optional[List[CacheDependency]] = None,
    cache_key_prefix: str = "",
    **kwargs,
) -> CacheDecoratorType:
    return cache(
        limit=limit,
        expire=expire,
        is_method=True,
        strict=strict,
        backend=DefaultConfig.get_current_config().CACHE_ALCHEMY_MEMORY_BACKEND,
        dependency=dependency or [],
        cache_key_prefix=cache_key_prefix,
        **kwargs,
    )


def property_memory_cache(
    limit: Optional[int] = None,
    *,
    expire: Optional[int] = None,
    strict: bool = False,
    dependency: Optional[List[CacheDependency]] = None,
    cache_key_prefix: str = "",
    **kwargs,
) -> CacheDecoratorType:
    return cache(
        limit=limit,
        expire=expire,
        is_method=True,
        strict=strict,
        backend=DefaultConfig.get_current_config().CACHE_ALCHEMY_MEMORY_BACKEND,
        dependency=dependency or [],
        cache_key_prefix=cache_key_prefix,
        **kwargs,
    )


def pickle_cache(
    limit: Optional[int] = None,
    *,
    expire: Optional[int] = None,
    is_method: bool = False,
    strict: bool = False,
    dependency: Optional[List[CacheDependency]] = None,
    cache_key_prefix: str = "",
    **kwargs,
) -> CacheDecoratorType:
    return cache(
        limit=limit,
        expire=expire,
        is_method=is_method,
        strict=strict,
        backend=DefaultConfig.get_current_config().CACHE_ALCHEMY_PICKLE_BACKEND,
        dependency=dependency or [],
        cache_key_prefix=cache_key_prefix,
        **kwargs,
    )


def method_pickle_cache(
    limit: Optional[int] = None,
    *,
    expire: Optional[int] = None,
    strict: bool = False,
    dependency: Optional[List[CacheDependency]] = None,
    cache_key_prefix: str = "",
    **kwargs,
) -> CacheDecoratorType:
    return cache(
        limit=limit,
        expire=expire,
        is_method=True,
        strict=strict,
        backend=DefaultConfig.get_current_config().CACHE_ALCHEMY_PICKLE_BACKEND,
        dependency=dependency or [],
        cache_key_prefix=cache_key_prefix,
        **kwargs,
    )


def property_pickle_cache(
    limit: Optional[int] = None,
    *,
    expire: Optional[int] = None,
    strict: bool = False,
    dependency: Optional[List[CacheDependency]] = None,
    cache_key_prefix: str = "",
    **kwargs,
) -> CacheDecoratorType:
    return cache(
        limit=limit,
        expire=expire,
        is_method=True,
        strict=strict,
        backend=DefaultConfig.get_current_config().CACHE_ALCHEMY_PICKLE_BACKEND,
        dependency=dependency or [],
        cache_key_prefix=cache_key_prefix,
        **kwargs,
    )
