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
    Union,
    cast,
    Pattern,
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
        return f"{self.cached_function.__qualname__}"

    @property
    def namespace(self) -> str:
        return f"{self.__class__.__name__}:{self.function_hash}-keys"

    @property
    def namespace_set(self) -> str:
        return f"{self.__class__.__name__}:all-keys"

    @abstractmethod
    def get(self, *args, **kwargs) -> ReturnType:  # pragma: no cover
        ...

    @abstractmethod
    def set(self, key: str, value: Any) -> None:  # pragma: no cover
        ...

    @abstractmethod
    def cache_clear(self, args: tuple, kwargs: dict) -> bool:  # pragma: no cover
        ...

    def cache_context(self, key: str) -> ContextManager:
        self.hits += 1
        return self

    def miss_context(self, key: str) -> ContextManager:
        self.misses += 1
        self.hits -= 1
        return self

    def make_key(
        self, args: Any, kwargs: Dict[str, Union[str, int]]
    ) -> Tuple[dict, dict, str]:
        keyword_args, kwargs, key = self.generate_key(
            args=args,
            kwargs=kwargs,
            func=self.cached_function,
            is_method=self.is_method,
        )
        return keyword_args, kwargs, f"{self.namespace}:{key}"

    def make_key_pattern(
        self, args: Any, kwargs: Dict[str, Union[str, int]]
    ) -> Pattern:
        pattern = self.generate_key_pattern(
            args=args,
            kwargs=kwargs,
            func=self.cached_function,
            is_method=self.is_method,
        )
        return re.compile(f"{re.escape(self.namespace)}:{pattern}", re.DOTALL)

    def __call__(self, *args, **kwargs):
        return self.get(*args, **kwargs)

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pass
