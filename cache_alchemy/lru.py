from threading import Lock

from cache_alchemy.link import DoublyLinkedListNode


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
            if key in self:
                # Getting here means that this same key was added to the
                # cache while the lock was released.  Since the link
                # update is already done, we need only return the
                # computed result and update the count of misses.
                pass
            elif self.full:
                # Use the old root to store the new key and result.
                oldroot: DoublyLinkedListNode = self.root
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
                self.root.mark_to_root()
                # Now update the cache dictionary.
                del self[oldkey]
                # Save the potentially reentrant cache[key] assignment
                # for last, after the root and links have been put in
                # a consistent state.
                super().__setitem__(key, oldroot)
            else:
                node = DoublyLinkedListNode(key=key, result=value)
                self.root.append_to_tail(node)
                super().__setitem__(key, node)

    def __getitem__(self, item):
        # Move the link to the front of the circular queue
        with self.lock:
            node: DoublyLinkedListNode = super().__getitem__(item)
            node.remove()
            self.root.append_to_tail(node)
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
