from timeit import timeit

from cache_alchemy.utils import generate_fast_key, generate_strict_key

__all__ = ["generate_fast_key", "generate_strict_key"]
tmp = lambda a, b=1, *, c, d=2, **kwd: ...


def benchmark():
    print(
        timeit(
            "fast_generate_key(args=(1,2), kwargs=dict(c=1,d=2), func=tmp)",
            globals=globals(),
        )
    )
    print(
        timeit(
            "strict_generate_key(args=(), kwargs=dict(a=1,b=2, c=1,d=2,e=3), func=tmp)",
            globals=globals(),
        )
    )


if __name__ == "__main__":
    benchmark()
