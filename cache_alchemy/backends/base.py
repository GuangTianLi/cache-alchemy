import re
from abc import ABC, abstractmethod
from types import FunctionType
from typing import (
    Any,
    ContextManager,
    Dict,
    Tuple,
    cast,
    Pattern,
)
from typing import Callable, TypeVar, Optional, Set, Generic

from ..config import DefaultConfig
from ..utils import (
    generate_strict_key,
    generate_fast_key,
    generate_strict_key_pattern,
    generate_fast_key_pattern,
)

ReturnType = TypeVar("ReturnType")
CacheFunctionType = Callable[..., ReturnType]


class BaseCache(Generic[ReturnType], ABC):
    def __init__(
        self,
        *,
        cached_function: CacheFunctionType,
        expire: int,
        limit: int,
        is_method: bool = False,
        strict: bool = False,
        cache_key_prefix: str = "",
    ):
        self.cached_function = cast(FunctionType, cached_function)
        self.is_method = is_method
        self.expire = expire
        self.limit = limit
        self.hits = self.misses = 0
        self.generate_key = generate_strict_key if strict else generate_fast_key
        self.generate_key_pattern = (
            generate_strict_key_pattern if strict else generate_fast_key_pattern
        )
        self.cache_key_prefix = cache_key_prefix

    @property
    def function_hash(self) -> str:
        return f"{self.cache_key_prefix}{self.__class__.__name__}:{self.cached_function.__module__}:{self.cached_function.__qualname__}"

    @property
    def namespace(self) -> str:
        return f"{self.cache_key_prefix}{self.__class__.__module__}:{self.function_hash}-keys"

    @classmethod
    def get_backend_namespace(cls, cache_key_prefix: str = "") -> str:
        return f"{cache_key_prefix}{cls.__module__}:{cls.__name__}:all-keys"

    @abstractmethod
    def get(self, *args, **kwargs) -> ReturnType:  # pragma: no cover
        ...

    @abstractmethod
    def set(self, key: str, value: Any) -> None:  # pragma: no cover
        ...

    @abstractmethod
    def cache_clear(
        self, args: Optional[tuple] = None, kwargs: Optional[dict] = None
    ) -> int:  # pragma: no cover
        ...

    @classmethod
    @abstractmethod
    def get_all_namespace(
        cls, cache_key_prefix: str = ""
    ) -> Set[str]:  # pragma: no cover
        ...

    @classmethod
    @abstractmethod
    def flush_cache(cls) -> int:  # pragma: no cover
        ...

    def cache_context(self, key: str) -> ContextManager:
        self.hits += 1
        return self

    def miss_context(self, key: str) -> ContextManager:
        self.misses += 1
        self.hits -= 1
        return self

    def make_key(self, args: tuple, kwargs: Dict[str, Any]) -> Tuple[dict, dict, str]:
        keyword_args, kwargs, key = self.generate_key(
            args=args,
            kwargs=kwargs,
            func=self.cached_function,
            is_method=self.is_method,
        )
        return keyword_args, kwargs, f"{self.function_hash}:{key}"

    def make_key_pattern(
        self, args: Optional[tuple], kwargs: Optional[Dict[str, Any]]
    ) -> Pattern:
        pattern = self.generate_key_pattern(
            args=args or tuple(),
            kwargs=kwargs or {},
            func=self.cached_function,
            is_method=self.is_method,
        )
        return re.compile(f"{re.escape(self.function_hash)}:{pattern}", re.DOTALL)

    def __call__(self, *args, **kwargs):
        return self.get(*args, **kwargs)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass


DistributedCacheReturnType = TypeVar("DistributedCacheReturnType", bound=bytes)


class DistributedCache(BaseCache[DistributedCacheReturnType]):
    def __init__(self, *, cached_function: FunctionType, **kwargs):
        super().__init__(cached_function=cached_function, **kwargs)
        self.client = DefaultConfig.get_current_config().cache_redis_client
        if self.client.connection_pool.connection_kwargs.get("decode_responses"):
            raise ValueError(
                "Distributed cache client cannot decode response, set decode_responses to False"
            )

    def get(self, *args, **kwargs) -> DistributedCacheReturnType:
        keyword_args, kwargs, cache_key = self.make_key(args, kwargs)
        with self.cache_context(cache_key):
            result = self.client.get(cache_key)
            if result is None:
                with self.miss_context(cache_key):
                    value = self.cached_function(*args, **keyword_args, **kwargs)
                    self.set(cache_key, value)
                    return value
            else:
                return self.deserialize(result)  # type: ignore

    def set(self, key: str, value: DistributedCacheReturnType) -> None:
        self.client.sadd(
            self.get_backend_namespace(self.cache_key_prefix), self.namespace
        )
        value = self.serialize(value)
        while self.client.scard(self.namespace) >= self.limit:
            del_key = self.client.spop(self.namespace)
            if isinstance(del_key, bytes):
                self.client.delete(del_key.decode())

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
            delete_keys = set(
                filter(
                    pattern.match,
                    map(bytes.decode, self.client.smembers(self.namespace)),
                )
            )
            if delete_keys:
                self.client.delete(*delete_keys)
        else:
            with self.client.pipeline() as pipe:
                delete_keys = self.client.smembers(self.namespace)
                if delete_keys:
                    pipe.delete(*delete_keys)
                    pipe.srem(self.namespace, *delete_keys)
                pipe.srem(
                    self.get_backend_namespace(self.cache_key_prefix), self.namespace
                )
                pipe.execute()
        return len(delete_keys)

    @classmethod
    def get_all_namespace(cls, cache_key_prefix: str = "") -> Set[str]:
        client = DefaultConfig.get_current_config().cache_redis_client
        return client.smembers(cls.get_backend_namespace(cache_key_prefix))

    @classmethod
    def flush_cache(cls, cache_key_prefix: str = "") -> int:
        client = DefaultConfig.get_current_config().cache_redis_client
        count = 0
        with client.pipeline() as pipe:
            for namespace in cls.get_all_namespace(cache_key_prefix):
                delete_keys = client.smembers(namespace)
                if delete_keys:
                    pipe.delete(*delete_keys)
                    count += len(delete_keys)
                pipe.delete(namespace)
            else:
                pipe.execute()
        return count

    def serialize(
        self, value: DistributedCacheReturnType
    ) -> DistributedCacheReturnType:
        return value

    def deserialize(
        self, result: DistributedCacheReturnType
    ) -> DistributedCacheReturnType:
        return result
