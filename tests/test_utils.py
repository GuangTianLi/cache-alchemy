import re
import unittest
from typing import List, Tuple

from cache_alchemy.utils import (
    generate_strict_key,
    generate_fast_key,
    generate_strict_key_pattern,
    UnsupportedError,
    generate_fast_key_pattern,
    escape,
)


class UtilsTestCase(unittest.TestCase):
    def test_generate_strict_key(self):
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
            ("a'1'b2", dict(args=(), kwargs=dict(a="1", b=2), func=lambda **k: ...)),
            ("a'1'", dict(args=(), kwargs=dict(a="1"), func=lambda **k: ...)),
            ("", dict(args=(), kwargs=dict(), func=lambda **k: ...)),
            ("a01a12b2", dict(args=(1, 2), kwargs=dict(b=2), func=lambda *a, **k: ...)),
            ("a1b1", dict(args=(1,), kwargs=dict(), func=lambda a, b=1: ...)),
            ("a1b1", dict(args=(), kwargs=dict(a=1), func=lambda a, b=1: ...)),
            ("a1b2", dict(args=(1,), kwargs=dict(b=2), func=lambda a, b=1: ...)),
            ("a'1'b'2'", dict(args=("1",), kwargs=dict(b="2"), func=lambda a, b: ...)),
            (
                "a'1'b'2'",
                dict(args=("1",), kwargs=dict(b="2"), func=lambda a, b="": ...),
            ),
            ("a1b2", dict(args=(1,), kwargs=dict(b=2), func=lambda a, *, b=1: ...)),
            ("a1b1", dict(args=(), kwargs=dict(), func=lambda a=1, b=1: ...)),
            ("a3b1", dict(args=(3,), kwargs=dict(), func=lambda a=1, b=1: ...)),
            ("a3b2", dict(args=(3,), kwargs=dict(b=2), func=lambda a=1, b=1: ...)),
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
                "a1b3",
                dict(
                    args=(tmp, 1, 3),
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
            with self.subTest(excepted_key=excepted_key, data=data):
                self.assertEqual(excepted_key, generate_strict_key(**data)[2])

    def test_generate_strict_key_pattern(self):
        class Tmp:
            @classmethod
            def tmp_class_method(cls, a, b=1):
                ...

            def tmp_method(self, a, b=1):
                ...

        tmp = Tmp()
        test_data: List[Tuple[str, dict, List[str], List[str]]] = [
            (".*?", dict(args=(), kwargs=dict(), func=lambda *a: ...), ["a02a13"], []),
            (
                "a01.*?",
                dict(args=(1,), kwargs=dict(), func=lambda *a: ...),
                ["a01a11"],
                ["a02a11"],
            ),
            (
                "a'1'b2.*?",
                dict(args=(), kwargs=dict(a="1", b=2), func=lambda **k: ...),
                ["a'1'b2c3"],
                ["a'2'b2c3"],
            ),
            (
                "a'1'.*?",
                dict(args=(), kwargs=dict(a="1"), func=lambda **k: ...),
                ["a'1'b2c3"],
                ["a2b2"],
            ),
            (
                "a01a12.*?b2.*?",
                dict(args=(1, 2), kwargs=dict(b=2), func=lambda *a, **k: ...),
                ["a01a12a23b2c3"],
                ["a02"],
            ),
            (
                "a1b.*?",
                dict(args=(1,), kwargs=dict(), func=lambda a, b: ...),
                ["a1b2"],
                ["a2b2"],
            ),
            (
                "a.*?b1",
                dict(args=(), kwargs=dict(b=1), func=lambda a, b: ...),
                ["a1b1"],
                ["a1b2"],
            ),
            (
                "a1b.*?",
                dict(args=(), kwargs=dict(a=1), func=lambda a, b: ...),
                ["a1b1"],
                ["a2b1"],
            ),
            (
                "a1b2",
                dict(args=(1,), kwargs=dict(b=2), func=lambda a, b: ...),
                ["a1b2"],
                ["a2b2", "a1b3"],
            ),
            (
                "a1b.*?",
                dict(args=(1,), kwargs=dict(), func=lambda a, b=1: ...),
                ["a1b1"],
                ["a2b2"],
            ),
            (
                "a1b1",
                dict(args=(1,), kwargs=dict(b=1), func=lambda a, b=1: ...),
                ["a1b1"],
                ["a2b2"],
            ),
            (
                "a1b2",
                dict(args=(1,), kwargs=dict(b=2), func=lambda a, *, b=1: ...),
                ["a1b2"],
                ["a2b2"],
            ),
            (
                "a1b.*?",
                dict(args=(1,), kwargs=dict(), func=lambda a, *, b=1: ...),
                ["a1b1"],
                ["a2b2"],
            ),
            (
                "a.*?b2",
                dict(args=(), kwargs=dict(b=2), func=lambda a=1, b=1: ...),
                ["a1b2"],
                ["a1b1"],
            ),
            (
                "a1b.*?",
                dict(args=(1,), kwargs=dict(), func=lambda a=1, b=1: ...),
                ["a1b1"],
                ["a2b2"],
            ),
            (
                f"cls{escape(str(Tmp))}a1b.*?",
                dict(args=(Tmp, 1), kwargs=dict(), func=tmp.tmp_class_method.__func__),
                [f"cls{Tmp}a1b1"],
                [f"cls{Tmp}a2b1"],
            ),
            (
                f"cls{escape(str(Tmp))}a1b2",
                dict(
                    args=(Tmp, 1), kwargs=dict(b=2), func=tmp.tmp_class_method.__func__
                ),
                [f"cls{Tmp}a1b2"],
                [f"cls{Tmp}a1b3"],
            ),
            (
                "a1b.*?",
                dict(
                    args=(tmp, 1),
                    kwargs=dict(),
                    func=tmp.tmp_method.__func__,
                    is_method=True,
                ),
                ["a1b1"],
                ["a2b2"],
            ),
            (
                "a1b3",
                dict(
                    args=(tmp, 1, 3),
                    kwargs=dict(),
                    func=tmp.tmp_method.__func__,
                    is_method=True,
                ),
                ["a1b3"],
                ["a2b3"],
            ),
            (
                "a1b2",
                dict(
                    args=(tmp, 1),
                    kwargs=dict(b=2),
                    func=tmp.tmp_method.__func__,
                    is_method=True,
                ),
                ["a1b2"],
                ["a2b3"],
            ),
        ]
        for excepted_pattern, data, hit_keys, miss_keys in test_data:
            with self.subTest(excepted_pattern=excepted_pattern, data=data):
                excepted_pattern += "$"
                self.assertEqual(
                    excepted_pattern,
                    generate_strict_key_pattern(**data),
                )
                pattern = re.compile(excepted_pattern, re.DOTALL)
                for key in hit_keys:
                    self.assertTrue(bool(pattern.match(key)))
                for key in miss_keys:
                    self.assertFalse(bool(pattern.match(key)))

    def test_generate_fast_key(self):
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
            with self.subTest(excepted_key=excepted_key, data=data):
                self.assertEqual(excepted_key, generate_fast_key(**data)[2])

    def test_generate_fast_key_pattern(self):
        with self.assertRaises(UnsupportedError):
            generate_fast_key_pattern(
                args=(), kwargs=dict(), func=lambda: None, is_method=True
            )


if __name__ == "__main__":
    unittest.main()
