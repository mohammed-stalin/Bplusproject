"""Regression and deterministic model-based tests; no third-party dependencies."""

import contextlib
import importlib
import io
import random
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from bplustree import BPlusTree, Bplustree
from utils import export_dot, format_tree, to_dot


class TreeTests(unittest.TestCase):
    def assert_valid(self, tree, expected):
        leaves, depths = [], set()

        def visit(node, parent, depth):
            self.assertIs(node.parent, parent)
            self.assertEqual(node.keys, sorted(set(node.keys)))
            self.assertLessEqual(len(node.keys), tree.degree - 1)
            if node.t == "leaf":
                if parent is not None:
                    self.assertGreaterEqual(len(node.keys), tree.degree // 2)
                leaves.append(node)
                depths.add(depth)
                return node.keys
            self.assertEqual(len(node.children), len(node.keys) + 1)
            self.assertGreaterEqual(len(node.children), 2 if parent is None else (tree.degree + 1) // 2)
            groups = [visit(child, node, depth + 1) for child in node.children]
            self.assertEqual(node.keys, [group[0] for group in groups[1:]])
            for left, right in zip(groups, groups[1:]):
                self.assertLess(left[-1], right[0])
            return [key for group in groups for key in group]

        self.assertEqual(visit(tree.root, None, 0), sorted(expected))
        self.assertEqual(len(depths), 1)
        for i, leaf in enumerate(leaves):
            self.assertIs(leaf.previous_leaf, leaves[i - 1] if i else None)
            self.assertIs(leaf.next_leaf, leaves[i + 1] if i + 1 < len(leaves) else None)
        self.assertEqual(list(tree), sorted(expected))
        self.assertEqual(len(tree), len(expected))

    def test_degree_validation(self):
        for degree in (True, False, 0, 1, 2, 3.5, "4", None):
            with self.subTest(degree=degree), self.assertRaises(ValueError):
                BPlusTree(degree)
        self.assertIs(BPlusTree, Bplustree)

    def test_empty_duplicate_and_single_key_deletion(self):
        tree = BPlusTree()
        self.assertFalse(tree.delete(4))
        self.assertEqual(tree.range_search(0, 10), [])
        self.assertTrue(tree.insert(4))
        self.assertFalse(tree.insert(4))
        self.assertEqual(tree.search(4, tree.root)[0::2], (0, 1))
        self.assertTrue(tree.delete(4))
        self.assert_valid(tree, set())
        self.assertEqual(tree.root.t, "leaf")

    def test_growth_and_complete_shrink(self):
        for degree in (3, 4, 5, 6, 7, 16):
            for reverse in (False, True):
                with self.subTest(degree=degree, reverse=reverse):
                    tree, expected = BPlusTree(degree), set()
                    for value in range(160):
                        self.assertTrue(tree.insert(value))
                        expected.add(value)
                        self.assert_valid(tree, expected)
                    for value in sorted(expected, reverse=reverse):
                        self.assertTrue(tree.delete(value))
                        expected.remove(value)
                        self.assert_valid(tree, expected)
                    self.assertEqual(tree.root.t, "leaf")

    def test_random_operations_against_set(self):
        for degree in (3, 4, 5, 6, 9, 16):
            for seed in range(4):
                rng = random.Random(seed)
                tree, expected = BPlusTree(degree), set()
                for _ in range(700):
                    value = rng.randrange(-100, 101)
                    if rng.random() < 0.55:
                        self.assertEqual(tree.insert(value), value not in expected)
                        expected.add(value)
                    else:
                        self.assertEqual(tree.delete(value), value in expected)
                        expected.discard(value)
                    self.assert_valid(tree, expected)
                    self.assertEqual(value in tree, value in expected)
                    lower, upper = sorted((rng.randrange(-120, 121), rng.randrange(-120, 121)))
                    self.assertEqual(tree.range_search(lower, upper),
                                     sorted(v for v in expected if lower <= v <= upper))
                self.assertEqual(tree.range_search(10, -10), [])

    def test_comparable_string_keys(self):
        tree = BPlusTree(3)
        for word in ("pear", "apple", "orange", "banana", "kiwi"):
            tree.insert(word)
        self.assertEqual(tree.range_search("banana", "orange"), ["banana", "kiwi", "orange"])
        self.assertTrue(tree.delete("orange"))
        self.assert_valid(tree, {"pear", "apple", "banana", "kiwi"})

    def test_export_and_text_view(self):
        tree = BPlusTree(3)
        for value in range(8):
            tree.insert(value)
        self.assertIn("Node", format_tree(tree.root))
        self.assertIn("Leaf", format_tree(tree.root))
        dot = to_dot(tree)
        self.assertEqual(dot, to_dot(tree))
        self.assertIn("style=dashed", dot)
        with tempfile.TemporaryDirectory() as directory:
            path = export_dot(tree, Path(directory) / "tree.dot")
            self.assertEqual(path.read_text(encoding="utf-8"), dot)

    def test_imports_have_no_interactive_side_effects(self):
        with patch("builtins.input", side_effect=AssertionError("interactive import")):
            importlib.import_module("main")
        # The GUI module needs Tkinter, so its import is checked only if available.
        try:
            import tkinter
        except ImportError:
            return
        with patch.object(tkinter.Tk, "__init__", side_effect=AssertionError("GUI import")):
            importlib.import_module("script")

    def test_terminal_workflow(self):
        root = Path(__file__).resolve().parents[1]
        result = subprocess.run(
            [sys.executable, str(root / "main.py")],
            input="oops\n1\nbad\n1\n8\n1\n8\n5\n8\n6\n0\n10\n2\n8\n2\n8\n3\n4\n",
            text=True, capture_output=True, check=True, cwd=root,
        )
        for message in ("valid integer", "Inserted.", "Already present.", "Found.",
                        "[8]", "Deleted.", "Value not found.", "Leaf []"):
            self.assertIn(message, result.stdout)

    def test_terminal_eof_and_invalid_degree(self):
        import main
        with patch("builtins.input", side_effect=EOFError), contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(main.main([]), 0)
        with contextlib.redirect_stderr(io.StringIO()), self.assertRaises(SystemExit) as error:
            main.main(["--degree", "2"])
        self.assertEqual(error.exception.code, 2)


if __name__ == "__main__":
    unittest.main()
