"""Dependency-free text and Graphviz DOT representations."""

from pathlib import Path


def format_tree(node, indent="   ", depth=0):
    label = "Leaf" if node.t == "leaf" else "Node"
    lines = [f"{indent * depth}{label} {node.keys}"]
    if node.t != "leaf":
        lines.extend(format_tree(child, indent, depth + 1) for child in node.children)
    return "\n".join(lines)


def print_tree(node, dl="   ", count=0):
    print(format_tree(node, dl, count))


def to_dot(tree):
    """Create deterministic DOT source, including dashed leaf links."""
    import json

    lines = ["digraph BPlusTree {", "  rankdir=TB;", '  node [shape=box, fontname="Helvetica"];']
    leaves = []

    def visit(node):
        name = f"n{visit.count}"
        visit.count += 1
        label = " | ".join(map(str, node.keys)) or "(empty)"
        lines.append(f"  {name} [label={json.dumps(label)}];")
        if node.t == "leaf":
            leaves.append(name)
        else:
            for child in node.children:
                child_name = visit(child)
                lines.append(f"  {name} -> {child_name};")
        return name

    visit.count = 0
    visit(tree.root)
    if leaves:
        lines.append("  { rank=same; " + "; ".join(leaves) + "; }")
    for left, right in zip(leaves, leaves[1:]):
        lines.append(f"  {left} -> {right} [style=dashed, constraint=false];")
    return "\n".join(lines + ["}"]) + "\n"


def export_dot(tree, path):
    path = Path(path)
    path.write_text(to_dot(tree), encoding="utf-8")
    return path
