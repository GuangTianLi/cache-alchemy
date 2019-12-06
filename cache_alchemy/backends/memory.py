import time
from typing import Any, Callable, Dict, TypeVar, Set, Optional

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


all_cache_pool: Dict[str, Dict] = {}


class MemoryCache(BaseCache):
    cache_pool: Dict[str, CacheItem]

    def __init__(self, *, cached_function: FunctionType, **kwargs):
        super().__init__(cached_function=cached_function, **kwargs)
        if self.limit == -1:
            self.cache_pool = dict()
        else:
            self.cache_pool = LRUDict(self.limit)
        self.post_init()

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
        all_cache_pool[self.namespace] = self.cache_pool
        timestamp = int(time.time()) + self.expire
        self.cache_pool[key] = CacheItem(timestamp=timestamp, value=value)

    def cache_clear(
        self, args: Optional[tuple] = None, kwargs: Optional[dict] = None
    ) -> int:
        if args or kwargs:
            pattern = self.make_key_pattern(args=args, kwargs=kwargs,)
            count = 0
            for key in filter(pattern.match, list(self.cache_pool.keys())):
                del self.cache_pool[key]
                count += 1
        else:
            count = len(self.cache_pool)
            self.cache_pool.clear()
        return count

    @classmethod
    def get_all_namespace(cls) -> Set[str]:
        return set(all_cache_pool.keys())

    @classmethod
    def flush_cache(cls) -> int:
        count = 0
        for cache_pool in all_cache_pool.values():
            count += len(cache_pool)
            cache_pool.clear()
        return count

    def __del__(self):
        all_cache_pool.pop(self.namespace, None)


class DistributedMemoryCache(MemoryCache, DistributedCache):
    def get(self, *args, **kwargs) -> ReturnType:
        return MemoryCache.get(self, *args, **kwargs)

    def set(self, key: str, value: Any) -> None:
        self.client.sadd(self.get_backend_namespace(), self.namespace)
        timestamp = int(time.time())
        DistributedCache.set(self, key, timestamp)
        self.cache_pool[key] = CacheItem(timestamp=timestamp, value=value)

    def get_timestamp(self, cache_key: str) -> int:
        timestamp = self.client.get(cache_key) or 0
        return int(timestamp)
