"""Interactive terminal interface: python main.py --degree 4."""

import argparse

from bplustree import BPlusTree
from utils import export_dot, print_tree


def main(argv=None):
    parser = argparse.ArgumentParser(description="Explore an in-memory B+ tree.")
    parser.add_argument("--degree", type=int, default=4, help="maximum fanout (at least 3)")
    args = parser.parse_args(argv)
    try:
        tree = BPlusTree(args.degree)
    except ValueError as error:
        parser.error(str(error))
    menu = (
        "\n1 Insert  2 Delete  3 Display  4 Exit\n"
        "5 Search  6 Range search  7 Export DOT"
    )
    while True:
        try:
            print(menu)
            choice = input("Choice: ").strip()
            if choice == "4":
                return 0
            if choice in {"1", "2", "5"}:
                value = int(input("Integer value: "))
                if choice == "1":
                    print("Inserted." if tree.insert(value) else "Already present.")
                elif choice == "2":
                    print("Deleted." if tree.delete(value) else "Value not found.")
                else:
                    print("Found." if value in tree else "Value not found.")
            elif choice == "3":
                print_tree(tree.root)
                print(f"Keys: {list(tree)} | Count: {len(tree)}")
            elif choice == "6":
                lower = int(input("Lower bound: "))
                upper = int(input("Upper bound: "))
                print(tree.range_search(lower, upper))
            elif choice == "7":
                path = input("DOT path [bplus_tree.dot]: ").strip() or "bplus_tree.dot"
                print(f"Saved {export_dot(tree, path)}")
            else:
                print("Choose an option from 1 through 7.")
        except ValueError:
            print("Please enter a valid integer.")
        except OSError as error:
            print(f"Could not save file: {error}")
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye.")
            return 0


if __name__ == "__main__":
    raise SystemExit(main())
