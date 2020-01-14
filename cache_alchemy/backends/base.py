import re
from abc import ABC, abstractmethod
from types import FunctionType
from typing import (
    Any,
    Callable,
    ContextManager,
    Dict,
    Tuple,
    TypeVar,
    cast,
    Pattern,
    Set,
    Optional,
)

from ..utils import (
    generate_strict_key,
    generate_fast_key,
    generate_strict_key_pattern,
    generate_fast_key_pattern,
)

ReturnType = TypeVar("ReturnType")
CacheFunctionType = Callable[..., ReturnType]


class BaseCache(ABC):
    def __init__(
        self,
        *,
        cached_function: CacheFunctionType,
        expire: int,
        limit: int,
        is_method: bool = False,
        strict=False,
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

    @property
    def function_hash(self) -> str:
        return f"{self.__class__.__name__}:{self.cached_function.__module__}:{self.cached_function.__qualname__}"

    @property
    def namespace(self) -> str:
        return f"{self.__class__.__module__}:{self.function_hash}-keys"

    @classmethod
    def get_backend_namespace(cls) -> str:
        return f"{cls.__module__}:{cls.__name__}:all-keys"

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
    def get_all_namespace(cls) -> Set[str]:  # pragma: no cover
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
