"""B+ tree supporting ordered, unique, mutually comparable keys."""

from bisect import bisect_left, bisect_right

from .node import Leaf, Node


class Bplustree:
    """A set-like B+ tree whose degree is the maximum internal fanout.

    Non-root leaves hold ceil((degree - 1) / 2) through degree - 1 keys.
    Non-root internal nodes hold ceil(degree / 2) through degree children.
    """

    def __init__(self, degree=4):
        if isinstance(degree, bool) or not isinstance(degree, int) or degree < 3:
            raise ValueError("degree must be an integer of at least 3")
        self.degree = degree
        self.root = Leaf(degree=degree)
        self._size = 0

    def __len__(self):
        return self._size

    def search(self, value, node=None):
        """Return (index, leaf, found); preserve the original search contract."""
        node = self.root if node is None else node
        while node.t != "leaf":
            node = node.children[bisect_right(node.keys, value)]
        index = bisect_left(node.keys, value)
        found = index < len(node.keys) and node.keys[index] == value
        return (index if found else 0), node, int(found)

    def __contains__(self, value):
        return bool(self.search(value)[2])

    def __iter__(self):
        """Yield ascending keys. Do not mutate the tree during iteration."""
        node = self.root
        while node.t != "leaf":
            node = node.children[0]
        while node is not None:
            yield from node.keys
            node = node.next_leaf

    def range_search(self, lower, upper):
        """Return all keys in the inclusive interval [lower, upper]."""
        if lower > upper:
            return []
        _, leaf, _ = self.search(lower)
        index = bisect_left(leaf.keys, lower)
        result = []
        while leaf is not None:
            for position in range(index, len(leaf.keys)):
                key = leaf.keys[position]
                if key > upper:
                    return result
                result.append(key)
            leaf = leaf.next_leaf
            index = 0
        return result

    @staticmethod
    def _refresh_up(node):
        while node is not None:
            node.refresh()
            node = node.parent

    def insert(self, value):
        """Insert a unique key; return False if it already exists."""
        _, leaf, found = self.search(value)
        if found:
            return False
        leaf.keys.insert(bisect_left(leaf.keys, value), value)
        self._size += 1
        if len(leaf.keys) < self.degree:
            self._refresh_up(leaf.parent)
            return True
        split = (len(leaf.keys) + 1) // 2
        right = Leaf(leaf, leaf.next_leaf, leaf.parent, self.degree)
        right.keys = leaf.keys[split:]
        leaf.keys = leaf.keys[:split]
        if right.next_leaf is not None:
            right.next_leaf.previous_leaf = right
        leaf.next_leaf = right
        self._attach_right(leaf, right)
        return True

    def _attach_right(self, left, right):
        parent = left.parent
        if parent is None:
            parent = Node(degree=self.degree)
            parent.children = [left, right]
            left.parent = right.parent = parent
            parent.refresh()
            self.root = parent
            return
        parent.children.insert(parent.children.index(left) + 1, right)
        right.parent = parent
        parent.refresh()
        if len(parent.children) <= self.degree:
            self._refresh_up(parent.parent)
            return
        split = (len(parent.children) + 1) // 2
        sibling = Node(parent.parent, self.degree)
        sibling.children = parent.children[split:]
        parent.children = parent.children[:split]
        for child in sibling.children:
            child.parent = sibling
        parent.refresh()
        sibling.refresh()
        self._attach_right(parent, sibling)

    def delete(self, value):
        """Delete a key; return False if absent."""
        index, leaf, found = self.search(value)
        if not found:
            return False
        leaf.keys.pop(index)
        self._size -= 1
        self._rebalance(leaf)
        return True

    def _rebalance(self, node):
        if node is self.root:
            if node.t != "leaf" and len(node.children) == 1:
                self.root = node.children[0]
                self.root.parent = None
            elif node.t != "leaf":
                node.refresh()
            return

        is_leaf = node.t == "leaf"
        minimum = self.degree // 2 if is_leaf else (self.degree + 1) // 2
        items = node.keys if is_leaf else node.children
        parent = node.parent
        if len(items) >= minimum:
            self._refresh_up(parent)
            return

        index = parent.children.index(node)
        left = parent.children[index - 1] if index else None
        right = parent.children[index + 1] if index + 1 < len(parent.children) else None
        for sibling, from_left in ((left, True), (right, False)):
            if sibling is None:
                continue
            donor = sibling.keys if is_leaf else sibling.children
            if len(donor) > minimum:
                item = donor.pop(-1 if from_left else 0)
                items.insert(0, item) if from_left else items.append(item)
                if not is_leaf:
                    item.parent = node
                    sibling.refresh()
                    node.refresh()
                self._refresh_up(parent)
                return

        # Merge into the leftmost of the two adjacent siblings.
        target, source = (left, node) if left is not None else (node, right)
        if is_leaf:
            target.keys.extend(source.keys)
            target.next_leaf = source.next_leaf
            if source.next_leaf is not None:
                source.next_leaf.previous_leaf = target
        else:
            target.children.extend(source.children)
            for child in source.children:
                child.parent = target
            target.refresh()
        parent.children.remove(source)
        parent.refresh()
        self._rebalance(parent)


BPlusTree = Bplustree
