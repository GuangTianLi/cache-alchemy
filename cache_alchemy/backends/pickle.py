import pickle

from .base import DistributedCache, BaseCache, ReturnType


class DistributedPickleCache(DistributedCache, BaseCache[ReturnType]):
    def serialize(self, value: ReturnType) -> bytes:
        return pickle.dumps(value)

    def deserialize(self, result: bytes) -> ReturnType:
        return pickle.loads(result)
