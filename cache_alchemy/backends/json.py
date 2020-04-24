import json

from .base import DistributedCache, BaseCache, ReturnType


class DistributedJsonCache(DistributedCache, BaseCache[ReturnType]):
    def serialize(self, value: ReturnType) -> bytes:
        return json.dumps(value).encode()

    def deserialize(self, result: bytes) -> ReturnType:
        return json.loads(result.decode())
