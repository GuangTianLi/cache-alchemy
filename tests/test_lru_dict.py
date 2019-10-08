import unittest

from cache_alchemy.lru_dict import LRUDict, DoubleLink


class LRUDictTestCase(unittest.TestCase):
    def test_full(self):
        with self.assertRaises(TypeError):
            LRUDict(-1)
        lru_dict = LRUDict(1)
        lru_dict[1] = 1
        self.assertTrue(lru_dict.full)
        self.assertEqual(1, lru_dict[1])
        lru_dict[2] = 2
        self.assertFalse(1 in lru_dict)
        self.assertEqual(2, lru_dict[2])
        self.assertEqual("{2: 2}", str(lru_dict))
        self.assertEqual("{2: 2}", repr(lru_dict))

    def test_lru(self):
        lru_dict = LRUDict(5)
        for index in range(5):
            lru_dict[index] = index
        for index, value in zip(range(4, -1, -1), lru_dict.root):
            self.assertEqual(index, value)
        for index in range(4, -1, -1):
            self.assertEqual(index, lru_dict[index])
        for index, value in zip(range(5), lru_dict.root):
            self.assertEqual(index, value)
        lru_dict[5] = 5
        self.assertTrue(4 not in lru_dict)

    def test_double_link(self):
        root = DoubleLink()
        last = root.prev
        link = DoubleLink(prev=last, next=root, key="1", result=1)
        root.prev = last.next = link
        self.assertEqual([1], list(root))
        self.assertEqual("1", str(link))


if __name__ == "__main__":
    unittest.main()
