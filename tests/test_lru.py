import unittest

from cache_alchemy import LRUDict
from cache_alchemy.lru import DoublyLinkedListNode


class LRUTestCase(unittest.TestCase):
    def test_full(self):
        with self.assertRaises(ValueError):
            LRUDict(-1)
        lru_dict = LRUDict(2)
        lru_dict[1] = 1
        lru_dict[1] = 1
        lru_dict[2] = 2
        self.assertEqual(2, len(lru_dict.root))
        self.assertTrue(lru_dict.full)
        self.assertEqual(2, lru_dict[2])
        lru_dict[3] = 3
        self.assertFalse(1 in lru_dict)
        self.assertEqual(2, lru_dict[2])

    def test_lru_dict(self):
        lru_dict = LRUDict(5)
        for index in range(6):
            lru_dict[index] = index
        for index, link in zip(range(5, 0, -1), lru_dict.root):
            self.assertEqual(index, link.key)
        for index in range(5, 0, -1):
            self.assertEqual(index, lru_dict[index])
        for index, link in zip(range(5, 1), lru_dict.root):
            self.assertEqual(index, link.key)

    def test_lru_dict_clear(self):
        lru_dict = LRUDict(5)
        for index in range(5):
            lru_dict[index] = index
        lru_dict.clear()
        self.assertEqual(0, len(lru_dict.root))

    def test_double_link(self):
        root = DoublyLinkedListNode()
        last = root.prev
        link = DoublyLinkedListNode(key="1", result=1)
        link.prev = last
        link.next = root
        root.prev = last.next = link
        self.assertEqual([link], list(root))
        self.assertEqual(1, len(root))
        self.assertEqual("1", str(link))


if __name__ == "__main__":
    unittest.main()
