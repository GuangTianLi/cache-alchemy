import time
from typing import Any, Callable, Dict, TypeVar

from .base import BaseCache
from .redis import DistributedCache
from ..lru_dict import LRUDict

ReturnType = TypeVar("ReturnType")
FunctionType = Callable[..., ReturnType]


class CacheItem:
    __slots__ = ("timestamp", "value")

    def __init__(self, timestamp: int, value: Any):
        self.timestamp = timestamp
        self.value = value


class MemoryCache(BaseCache):
    cache_pool: Dict[str, CacheItem]

    def __init__(self, *, cached_function: FunctionType, **kwargs):
        super().__init__(cached_function=cached_function, **kwargs)
        if self.limit == -1:
            self.cache_pool = dict()
        else:
            self.cache_pool = LRUDict(self.limit)

    def get(self, *args, **kwargs) -> ReturnType:
        keyword_args, kwargs, cache_key = self.make_key(args, kwargs)
        with self.cache_context(cache_key):
            timestamp = self.get_timestamp(cache_key)
            cache_info = self.cache_pool.get(cache_key)
            if cache_info and timestamp <= cache_info.timestamp:
                return cache_info.value
            else:
                with self.miss_context(cache_key):
                    value = self.cached_function(*args, **keyword_args, **kwargs)
                    self.set(cache_key, value)
                    return value

    def get_timestamp(self, cache_key: str) -> int:
        return int(time.time())

    def set(self, key: str, value: Any) -> None:
        timestamp = int(time.time()) + self.expire
        self.cache_pool[key] = CacheItem(timestamp=timestamp, value=value)

    def cache_clear(self, args: tuple, kwargs: dict) -> bool:
        if args or kwargs:
            pattern = self.make_key_pattern(args=args, kwargs=kwargs,)
            for key in filter(pattern.match, list(self.cache_pool.keys())):
                del self.cache_pool[key]
        else:
            self.cache_pool.clear()
        return True


class DistributedMemoryCache(MemoryCache, DistributedCache):
    def __init__(self, *, cached_function: FunctionType, **kwargs):
        super().__init__(cached_function=cached_function, **kwargs)

    def get(self, *args, **kwargs) -> ReturnType:
        return MemoryCache.get(self, *args, **kwargs)

    def set(self, key: str, value: Any) -> None:
        self.client.sadd(self.namespace_set, self.namespace)
        timestamp = int(time.time())
        DistributedCache.set(self, key, timestamp)
        self.cache_pool[key] = CacheItem(timestamp=timestamp, value=value)

    def get_timestamp(self, cache_key: str) -> int:
        timestamp = self.client.get(cache_key) or 0
        return int(timestamp)
