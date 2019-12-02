from typing import TYPE_CHECKING
from weakref import ref

from configalchemy import BaseConfig

if TYPE_CHECKING:  # pragma: no cover
    from redis import StrictRedis

_current_config_ref = ref(object)


class DefaultConfig(BaseConfig):
    #: default redis url
    CACHE_ALCHEMY_REDIS_URL = "redis://127.0.0.1:6379/0"
    #: redis cache backend - default: distributed cache which need assign client to config
    CACHE_ALCHEMY_REDIS_BACKEND = "cache_alchemy.backends.redis.DistributedCache"
    #: redis memory backend - default: distributed cache which need assign client to config
    CACHE_ALCHEMY_MEMORY_BACKEND = (
        "cache_alchemy.backends.memory.DistributedMemoryCache"
    )
    #: default cache limit per function
    #: - setting to -1 means unlimited
    #: - setting to 0 means uncached
    CACHE_ALCHEMY_DEFAULT_LIMIT = 1000
    #: default cache expire time (seconds)
    #: - setting to 0 means uncached
    CACHE_ALCHEMY_DEFAULT_EXPIRE = 60 * 60 * 24

    #: Need to be assigned after init, if use distributed cache
    cache_redis_client: "StrictRedis"

    def __init__(self):
        super().__init__()
        global _current_config_ref
        _current_config_ref = ref(self)

    @classmethod
    def get_current_config(cls) -> "DefaultConfig":
        current_config = _current_config_ref()
        if not isinstance(current_config, cls):
            raise RuntimeError(f"There is no instance of type {DefaultConfig}")
        return current_config
