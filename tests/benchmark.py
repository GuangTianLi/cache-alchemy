from functools import _make_key
from timeit import timeit

from cache_alchemy.utils import generate_key as old_generate_key

tmp = lambda a, b=1, *, c, d=2, **kwd: ...


def make_key(args, kwds):
    return hash(_make_key(args=args, kwds=kwds, typed=False))


def generate_key(args, kwargs):
    old_generate_key(args=args, kwargs=kwargs, func=tmp)


def benchmark():
    print(timeit("make_key(args=(1,2), kwds=dict(c=1,d=2))", globals=globals()))
    print(
        timeit(
            "generate_key(args=(), kwargs=dict(a=1,b=2, c=1,d=2,e=3))",
            globals=globals(),
        )
    )


if __name__ == "__main__":
    benchmark()
