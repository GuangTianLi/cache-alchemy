from threading import Lock
from typing import Iterable

_sentry = object()


class DoublyLinkedListNode(Iterable):
    __slots__ = ("prev", "next", "key", "result")

    def __init__(
        self,
        key=_sentry,
        result=None,
    ):
        self.prev = self
        self.next = self
        self.key = key
        self.result = result

    def __iter__(self):
        if self.prev.key is _sentry:
            return
        yield self.prev
        yield from self.prev

    def __hash__(self):
        return hash(self.key)

    def __len__(self):
        return sum(map(lambda _: 1, self))

    def __repr__(self):
        return repr(self.result)

    def __str__(self):
        return str(self.result)


class LRUDict(dict):
    __slots__ = ("max_size", "root", "lock", "__weakref__")

    def __init__(self, max_size: int):
        if max_size <= 0:
            raise ValueError("Expected max_size to be larger than 0")
        self.max_size = max_size
        self.root = DoublyLinkedListNode()
        self.lock = Lock()
        super().__init__()

    @property
    def full(self) -> bool:
        return len(self) >= self.max_size

    def __setitem__(self, key, value):
        with self.lock:
            if self.full:
                # Use the old root to store the new key and result.
                oldroot = self.root
                oldroot.key = key
                oldroot.result = value
                # Empty the oldest link and make it the new root.
                # Keep a reference to the old key and old result to
                # prevent their ref counts from going to zero during the
                # update. That will prevent potentially arbitrary object
                # clean-up code (i.e. __del__) from running while we're
                # still adjusting the links.
                self.root = oldroot.next
                oldkey = self.root.key
                # Now update the cache dictionary.
                del self[oldkey]
                # Save the potentially reentrant cache[key] assignment
                # for last, after the root and links have been put in
                # a consistent state.
                super().__setitem__(key, oldroot)
            else:
                last = self.root.prev
                node = DoublyLinkedListNode(key=key, result=value)
                last.next = self.root.prev = node
                node.prev = last
                node.next = self.root
                super().__setitem__(key, node)

    def __getitem__(self, item):
        # Move the link to the front of the circular queue
        with self.lock:
            node = super().__getitem__(item)
            node.prev.next = node.next
            node.next.prev = node.prev
            last = self.root.prev
            last.next = self.root.prev = node
            node.prev = last
            node.next = self.root
            return node.result

    def get(self, k, default=None):
        """Use EAFP to avoid RLock"""
        try:
            return self[k]
        except KeyError:
            return default

    def clear(self):
        with self.lock:
            self.root = DoublyLinkedListNode()
            super().clear()
