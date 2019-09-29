import unittest

from cache_alchemy.lru_dict import LRUDict


class LRUDictTestCase(unittest.TestCase):
    def test_full(self):
        lru_dict = LRUDict(1)
        lru_dict[1] = 1
        self.assertTrue(lru_dict.full)
        self.assertEqual(1, lru_dict[1])
        lru_dict[2] = 2
        self.assertFalse(1 in lru_dict)
        self.assertEqual(2, lru_dict[2])

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


if __name__ == "__main__":
    unittest.main()
