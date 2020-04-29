from typing import Dict, Hashable, List, Set, Optional
from weakref import WeakSet

from .backends.base import BaseCache, CacheFunctionType


class CacheDependency:
    all_dependencies: Dict[Hashable, List["CacheDependency"]] = {}

    def __init__(self, ident: Hashable):
        self.ident = ident
        self.cache_objects: Set[BaseCache] = WeakSet()  # type: ignore

    @classmethod
    def register_dependency(cls, dependency: "CacheDependency") -> None:
        cls.all_dependencies.setdefault(dependency.ident, []).append(dependency)

    @classmethod
    def find_dependencies(cls, ident: Hashable) -> List["CacheDependency"]:
        return cls.all_dependencies.get(ident, [])

    @classmethod
    def dependent_cache_clear(
        cls,
        ident: Hashable,
        args: Optional[tuple] = None,
        kwargs: Optional[dict] = None,
    ) -> int:
        count = 0
        for dependency in cls.find_dependencies(ident):
            for cache in dependency.cache_objects:
                count += cache.cache_clear(args, kwargs)
        return count


class FunctionCacheDependency(CacheDependency):
    """
    Examples::

        @json_cache()
        def add(a, b):
            return a + b

        dependency = FunctionCacheDependency(add)

        @json_cache(dependency=[dependency])
        def add_and_double(a, b):
            return add(a, b) * 2
    """

    def __init__(self, cached_func: CacheFunctionType):
        super().__init__(ident=getattr(cached_func, "cache"))
