import json
from typing import Callable, TypeVar, Optional, Set

from configalchemy.types import JsonSerializable

from .base import BaseCache
from ..config import DefaultConfig

ReturnType = TypeVar("ReturnType", bound=JsonSerializable)
FunctionType = Callable[..., ReturnType]


class DistributedCache(BaseCache):
    def __init__(self, *, cached_function: FunctionType, **kwargs):
        super().__init__(cached_function=cached_function, **kwargs)
        self.client = DefaultConfig.get_current_config().cache_redis_client

    def get(self, *args, **kwargs) -> ReturnType:
        keyword_args, kwargs, cache_key = self.make_key(args, kwargs)
        with self.cache_context(cache_key):
            result: Optional[str] = self.client.get(cache_key)  # type: ignore
            if result is None:
                with self.miss_context(cache_key):
                    value = self.cached_function(*args, **keyword_args, **kwargs)
                    self.set(cache_key, value)
                    return value
            else:
                return self.process_result(result)

    def set(self, key: str, value: JsonSerializable) -> None:
        self.client.sadd(self.get_backend_namespace(), self.namespace)
        value = self.process_value(value)
        while self.client.scard(self.namespace) >= self.limit:
            del_key = self.client.spop(self.namespace)
            self.client.delete(del_key)

        with self.client.pipeline() as pipe:
            if self.expire == -1:
                pipe.set(key, value)
            else:
                pipe.setex(key, self.expire, value)

            pipe.sadd(self.namespace, key)
            pipe.execute()

    def cache_clear(
        self, args: Optional[tuple] = None, kwargs: Optional[dict] = None
    ) -> int:
        if args or kwargs:
            pattern = self.make_key_pattern(args=args, kwargs=kwargs)
            delete_keys = list(
                filter(pattern.match, self.client.smembers(self.namespace))
            )
            if delete_keys:
                self.client.delete(*delete_keys)
        else:
            with self.client.pipeline() as pipe:
                delete_keys = self.client.smembers(self.namespace)
                if delete_keys:
                    pipe.delete(*delete_keys)
                pipe.delete(self.namespace)
                pipe.srem(self.get_backend_namespace(), self.namespace)
                pipe.execute()
        return len(delete_keys)

    @classmethod
    def get_all_namespace(cls) -> Set[str]:
        client = DefaultConfig.get_current_config().cache_redis_client
        return client.smembers(cls.get_backend_namespace())

    @classmethod
    def flush_cache(cls) -> int:
        client = DefaultConfig.get_current_config().cache_redis_client
        count = 0
        with client.pipeline() as pipe:
            for namespace in cls.get_all_namespace():
                delete_keys = client.smembers(namespace)
                if delete_keys:
                    pipe.delete(*delete_keys)
                    count += len(delete_keys)
                pipe.delete(namespace)
            else:
                pipe.execute()
        return count

    def process_value(self, value: ReturnType) -> str:
        return json.dumps(value)

    def process_result(self, result: str) -> ReturnType:
        return json.loads(result)
