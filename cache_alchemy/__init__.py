"""
Caching framework.
"""

__version__ = "0.1.4"

from functools import wraps
from importlib import import_module
from types import FunctionType
from typing import Callable, List, Optional, cast, Type, TypeVar

from .backends.base import BaseCache, CacheFunctionType
from .config import DefaultConfig
from .dependency import CacheDependency

__all__ = ["redis_cache", "memory_cache", "cache", "CacheDecoratorType"]

BackendCls = TypeVar("BackendCls", bound=BaseCache)


def _create_cache(
    *,
    backend_cls: Type[BackendCls],
    cached_function: FunctionType,
    expire: Optional[int],
    limit: Optional[int],
    is_method: bool = False,
    strict=False,
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
    **kwargs,
) -> CacheDecoratorType:
    """

    :param bool is_method: If *True*, the first argument will be ignored in generate cache key.
    """
    config = DefaultConfig.get_current_config()
    module_path, class_name = backend.rsplit(".", 1)
    backend_cls = getattr(import_module(module_path), class_name)

    if limit is None:
        limit = config.CACHE_ALCHEMY_DEFAULT_LIMIT
    if expire is None:
        expire = config.CACHE_ALCHEMY_DEFAULT_EXPIRE

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
            **kwargs,
        )

        @wraps(func)
        def wrapper(*args, **kwargs):
            return cache(*args, **kwargs)

        def cache_clear():
            """Clear the cache and cache statistics"""
            cache.cache_clear()
            CacheDependency.dependent_cache_clear(cache)

        for item in dependency:
            item.cache_objects.add(cache)
            item.register_dependency(item)

        wrapper.cache = cache  # type: ignore
        wrapper.cache_clear = cache_clear  # type: ignore
        return wrapper

    if callable(limit):
        user_function, limit = limit, config.CACHE_ALCHEMY_DEFAULT_LIMIT
        return decorating_function(user_function)
    return decorating_function


def redis_cache(
    limit: Optional[int] = None,
    *,
    expire: Optional[int] = None,
    is_method: bool = False,
    strict: bool = False,
    dependency: Optional[List[CacheDependency]] = None,
) -> CacheDecoratorType:
    return cache(
        limit=limit,
        expire=expire,
        is_method=is_method,
        strict=strict,
        backend=DefaultConfig.get_current_config().CACHE_ALCHEMY_REDIS_BACKEND,
        dependency=dependency or [],
    )


def memory_cache(
    limit: Optional[int] = None,
    *,
    expire: Optional[int] = None,
    is_method: bool = False,
    strict: bool = False,
    dependency: Optional[List[CacheDependency]] = None,
) -> CacheDecoratorType:
    return cache(
        limit=limit,
        expire=expire,
        is_method=is_method,
        strict=strict,
        backend=DefaultConfig.get_current_config().CACHE_ALCHEMY_MEMORY_BACKEND,
        dependency=dependency or [],
    )


def method_memory_cache(
    limit: Optional[int] = None,
    *,
    expire: Optional[int] = None,
    strict: bool = False,
    dependency: Optional[List[CacheDependency]] = None,
) -> CacheDecoratorType:
    return cache(
        limit=limit,
        expire=expire,
        is_method=True,
        strict=strict,
        backend=DefaultConfig.get_current_config().CACHE_ALCHEMY_MEMORY_BACKEND,
        dependency=dependency or [],
    )


def method_redis_cache(
    limit: Optional[int] = None,
    *,
    expire: Optional[int] = None,
    strict: bool = False,
    dependency: Optional[List[CacheDependency]] = None,
) -> CacheDecoratorType:
    return cache(
        limit=limit,
        expire=expire,
        is_method=True,
        strict=strict,
        backend=DefaultConfig.get_current_config().CACHE_ALCHEMY_REDIS_BACKEND,
        dependency=dependency or [],
    )


def property_memory_cache(
    limit: Optional[int] = None,
    *,
    expire: Optional[int] = None,
    strict: bool = False,
    dependency: Optional[List[CacheDependency]] = None,
) -> CacheDecoratorType:
    return cache(
        limit=limit,
        expire=expire,
        is_method=True,
        strict=strict,
        backend=DefaultConfig.get_current_config().CACHE_ALCHEMY_MEMORY_BACKEND,
        dependency=dependency or [],
    )


def property_redis_cache(
    limit: Optional[int] = None,
    *,
    expire: Optional[int] = None,
    strict: bool = False,
    dependency: Optional[List[CacheDependency]] = None,
) -> CacheDecoratorType:
    return cache(
        limit=limit,
        expire=expire,
        is_method=True,
        strict=strict,
        backend=DefaultConfig.get_current_config().CACHE_ALCHEMY_REDIS_BACKEND,
        dependency=dependency or [],
    )
