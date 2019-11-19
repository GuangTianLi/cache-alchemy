import unittest
from typing import List, Tuple

from cache_alchemy.utils import strict_generate_key, fast_generate_key


class UtilsTestCase(unittest.TestCase):
    def test_strict_generate_key(self):
        class Tmp:
            @classmethod
            def tmp_class_method(cls, a, b=1):
                ...

            def tmp_method(self, a, b=1):
                ...

        tmp = Tmp()
        test_data: List[Tuple[str, dict]] = [
            ("", dict(args=(), kwargs=dict(), func=lambda *a: ...)),
            ("a01", dict(args=(1,), kwargs=dict(), func=lambda *a: ...)),
            ("a01a12", dict(args=(1, 2), kwargs=dict(), func=lambda *a: ...)),
            ("a1b2", dict(args=(), kwargs=dict(a="1", b=2), func=lambda **k: ...)),
            ("a1", dict(args=(), kwargs=dict(a="1"), func=lambda **k: ...)),
            ("", dict(args=(), kwargs=dict(), func=lambda **k: ...)),
            ("a01a12b2", dict(args=(1, 2), kwargs=dict(b=2), func=lambda *a, **k: ...)),
            ("a1b1", dict(args=(1,), kwargs=dict(), func=lambda a, b=1: ...)),
            ("a1b1", dict(args=(), kwargs=dict(a=1), func=lambda a, b=1: ...)),
            ("a1b2", dict(args=(1,), kwargs=dict(b=2), func=lambda a, b=1: ...)),
            ("a1b2", dict(args=(1,), kwargs=dict(b=2), func=lambda a, *, b=1: ...)),
            ("a1b2", dict(args=(1,), kwargs=dict(b=2), func=lambda a=1, b=1: ...)),
            ("a1b2", dict(args=(), kwargs=dict(b=2), func=lambda a=1, b=1: ...)),
            (
                f"cls{Tmp}a1b1",
                dict(args=(Tmp, 1), kwargs=dict(), func=tmp.tmp_class_method.__func__),
            ),
            (
                f"cls{Tmp}a1b2",
                dict(
                    args=(Tmp, 1), kwargs=dict(b=2), func=tmp.tmp_class_method.__func__
                ),
            ),
            (
                "a1b1",
                dict(
                    args=(tmp, 1),
                    kwargs=dict(),
                    func=tmp.tmp_method.__func__,
                    is_method=True,
                ),
            ),
            (
                "a1b2",
                dict(
                    args=(tmp, 1),
                    kwargs=dict(b=2),
                    func=tmp.tmp_method.__func__,
                    is_method=True,
                ),
            ),
        ]
        for excepted_key, data in test_data:
            self.assertEqual(excepted_key, strict_generate_key(**data)[2])

    def test_fast_generate_key(self):
        class Tmp:
            @classmethod
            def tmp_class_method(cls, a, b=1):
                ...

            def tmp_method(self, a, b=1):
                ...

        tmp = Tmp()
        test_data: List[Tuple[str, dict]] = [
            ("()", dict(args=(), kwargs=dict(), func=lambda *a: ...)),
            ("(1,)", dict(args=(1,), kwargs=dict(), func=lambda *a: ...)),
            ("(1, 2)", dict(args=(1, 2), kwargs=dict(), func=lambda *a: ...)),
            (
                "('a', '1', 'b', 2)",
                dict(args=(), kwargs=dict(a="1", b=2), func=lambda **k: ...),
            ),
            ("('a', '1')", dict(args=(), kwargs=dict(a="1"), func=lambda **k: ...)),
            ("()", dict(args=(), kwargs=dict(), func=lambda **k: ...)),
            (
                "(1, 2, 'b', 2)",
                dict(args=(1, 2), kwargs=dict(b=2), func=lambda *a, **k: ...),
            ),
            ("(1,)", dict(args=(1,), kwargs=dict(), func=lambda a, b=1: ...)),
            ("('a', 1)", dict(args=(), kwargs=dict(a=1), func=lambda a, b=1: ...)),
            ("(1, 'b', 2)", dict(args=(1,), kwargs=dict(b=2), func=lambda a, b=1: ...)),
            (
                "(1, 'b', 2)",
                dict(args=(1,), kwargs=dict(b=2), func=lambda a, *, b=1: ...),
            ),
            (
                "(1, 'b', 2)",
                dict(args=(1,), kwargs=dict(b=2), func=lambda a=1, b=1: ...),
            ),
            ("('b', 2)", dict(args=(), kwargs=dict(b=2), func=lambda a=1, b=1: ...)),
            (
                f"({Tmp}, 1)",
                dict(args=(Tmp, 1), kwargs=dict(), func=tmp.tmp_class_method.__func__),
            ),
            (
                f"({Tmp}, 1, 'b', 2)",
                dict(
                    args=(Tmp, 1), kwargs=dict(b=2), func=tmp.tmp_class_method.__func__
                ),
            ),
            (
                "(1,)",
                dict(
                    args=(tmp, 1),
                    kwargs=dict(),
                    func=tmp.tmp_method.__func__,
                    is_method=True,
                ),
            ),
            (
                "(1, 'b', 2)",
                dict(
                    args=(tmp, 1),
                    kwargs=dict(b=2),
                    func=tmp.tmp_method.__func__,
                    is_method=True,
                ),
            ),
        ]
        for excepted_key, data in test_data:
            self.assertEqual(excepted_key, fast_generate_key(**data)[2])


if __name__ == "__main__":
    unittest.main()
