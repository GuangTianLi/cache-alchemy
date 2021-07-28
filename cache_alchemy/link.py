from typing import Iterable

_sentry = object()


class DoublyLinkedListNode(Iterable):
    __slots__ = ("prev", "next", "key", "result")

    def __init__(self, key=_sentry, result=None):
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

    def remove(self):
        self.prev.next = self.next
        self.next.prev = self.prev

    def append_to_tail(self, node: "DoublyLinkedListNode"):
        last = self.prev
        last.next = self.prev = node
        node.prev = last
        node.next = self

    def mark_to_root(self):
        self.key = _sentry
        self.result = _sentry
