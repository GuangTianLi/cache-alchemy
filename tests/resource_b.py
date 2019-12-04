from unittest.mock import MagicMock

from cache_alchemy import redis_cache, memory_cache
from tests import get_config

redis_call_mock = MagicMock()

config = get_config()


@redis_cache
def redis_test():
    redis_call_mock()
    return "test"


memory_call_mock = MagicMock()


@memory_cache
def memory_test():
    memory_call_mock()
    return "test"
