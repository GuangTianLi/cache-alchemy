from unittest.mock import MagicMock
from tests import get_config
from cache_alchemy import json_cache, memory_cache

redis_call_mock = MagicMock()

config = get_config()


@json_cache()
def json_test():
    redis_call_mock()
    return "test"


memory_call_mock = MagicMock()


@memory_cache()
def memory_test():
    memory_call_mock()
    return "test"
