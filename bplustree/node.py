"""Structural nodes for an in-memory B+ tree."""


class Node:
    """Internal node; separators are minima of the children to their right."""

    t = "node"

    def __init__(self, parent=None, degree=4):
        self.parent = parent
        self.degree = degree
        self.keys = []
        self.children = []

    @property
    def minimum(self):
        node = self
        while node.t != "leaf":
            node = node.children[0]
        return node.keys[0]

    def refresh(self):
        self.keys = [child.minimum for child in self.children[1:]]


class Leaf(Node):
    """Sorted unique keys with a doubly linked chain for range scans."""

    t = "leaf"

    def __init__(self, previous_leaf=None, next_leaf=None, parent=None, degree=4):
        super().__init__(parent, degree)
        self.previous_leaf = previous_leaf
        self.next_leaf = next_leaf

    def size(self):
        return len(self.keys)
