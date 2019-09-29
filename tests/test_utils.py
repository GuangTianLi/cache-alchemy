import unittest

from cache_alchemy.utils import generate_key


class UtilsTestCase(unittest.TestCase):
    def test_generate_key(self):
        self.assertEqual(
            "", generate_key(args=(), kwargs=dict(), func=lambda *a: ...)[2]
        )
        self.assertEqual(
            "a01", generate_key(args=(1,), kwargs=dict(), func=lambda *a: ...)[2]
        )
        self.assertEqual(
            "a01a12", generate_key(args=(1, 2), kwargs=dict(), func=lambda *a: ...)[2]
        )
        self.assertEqual(
            "a1b2",
            generate_key(args=(), kwargs=dict(a="1", b=2), func=lambda **k: ...)[2],
        )
        self.assertEqual(
            "a1", generate_key(args=(), kwargs=dict(a="1"), func=lambda **k: ...)[2]
        )
        self.assertEqual(
            "", generate_key(args=(), kwargs=dict(), func=lambda **k: ...)[2]
        )
        self.assertEqual(
            "a01a12b2",
            generate_key(args=(1, 2), kwargs=dict(b=2), func=lambda *a, **k: ...)[2],
        )
        self.assertEqual(
            "a1b1", generate_key(args=(1,), kwargs=dict(), func=lambda a, b=1: ...)[2]
        )
        self.assertEqual(
            "a1b1", generate_key(args=(), kwargs=dict(a=1), func=lambda a, b=1: ...)[2]
        )
        self.assertEqual(
            "a1b2",
            generate_key(args=(1,), kwargs=dict(b=2), func=lambda a, b=1: ...)[2],
        )
        self.assertEqual(
            "a1b2",
            generate_key(args=(1,), kwargs=dict(b=2), func=lambda a=1, b=1: ...)[2],
        )
        self.assertEqual(
            "a1b2",
            generate_key(args=(), kwargs=dict(b=2), func=lambda a=1, b=1: ...)[2],
        )

        class Tmp:
            @classmethod
            def tmp_class_method(cls, a, b=1):
                ...

            def tmp_method(self, a, b=1):
                ...

        tmp = Tmp()
        self.assertEqual(
            f"cls{Tmp}a1b1",
            generate_key(
                args=(Tmp, 1), kwargs=dict(), func=tmp.tmp_class_method.__func__
            )[2],
        )
        self.assertEqual(
            f"cls{Tmp}a1b2",
            generate_key(
                args=(Tmp, 1), kwargs=dict(b=2), func=tmp.tmp_class_method.__func__
            )[2],
        )
        self.assertEqual(
            "a1b1",
            generate_key(
                args=(tmp, 1),
                kwargs=dict(),
                func=tmp.tmp_method.__func__,
                is_method=True,
            )[2],
        )
        self.assertEqual(
            "a1b2",
            generate_key(
                args=(tmp, 1),
                kwargs=dict(b=2),
                func=tmp.tmp_method.__func__,
                is_method=True,
            )[2],
        )


if __name__ == "__main__":
    unittest.main()
