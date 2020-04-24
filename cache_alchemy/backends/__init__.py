import dataclasses
import pickle
import redis


@dataclasses.dataclass
class T:
    name: str


r = redis.Redis(decode_responses=True)
t = T(name="test")

data = pickle.dumps(t)
