"""Tkinter explorer with live text visualization and optional DOT export."""

import tkinter as tk
from tkinter import filedialog, messagebox, ttk

from bplustree import BPlusTree
from utils import export_dot, format_tree


class BPlusTreeGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("B+ Tree Explorer")
        self.geometry("850x600")
        self.minsize(650, 420)
        self.tree = BPlusTree(4)
        frame = ttk.Frame(self, padding=16)
        frame.pack(fill="both", expand=True)
        ttk.Label(frame, text="B+ Tree Explorer", font=("Segoe UI", 20, "bold")).pack(anchor="w")
        ttk.Label(frame, text="Insert, delete and search integer keys. The view updates after each operation.").pack(anchor="w", pady=(4, 12))
        controls = ttk.Frame(frame)
        controls.pack(fill="x")
        ttk.Label(controls, text="Key:").pack(side="left")
        self.entry = ttk.Entry(controls, width=16)
        self.entry.pack(side="left", padx=8)
        for label, action in (("Insert", self.add_value), ("Delete", self.delete_value),
                              ("Search", self.search_value), ("Export DOT", self.export_tree)):
            ttk.Button(controls, text=label, command=action).pack(side="left", padx=3)
        self.entry.bind("<Return>", lambda event: self.add_value())
        ranges = ttk.Frame(frame)
        ranges.pack(fill="x", pady=10)
        ttk.Label(ranges, text="Inclusive range:").pack(side="left")
        self.lower = ttk.Entry(ranges, width=12)
        self.lower.pack(side="left", padx=8)
        self.upper = ttk.Entry(ranges, width=12)
        self.upper.pack(side="left", padx=8)
        ttk.Button(ranges, text="Find range", command=self.range_values).pack(side="left")
        self.output = tk.Text(frame, wrap="none", font=("Consolas", 11))
        scrollbar = ttk.Scrollbar(frame, command=self.output.yview)
        scrollbar.pack(side="right", fill="y")
        self.output.configure(yscrollcommand=scrollbar.set)
        self.output.pack(fill="both", expand=True)
        self.status = tk.StringVar(value="Ready. Degree: 4.")
        ttk.Label(frame, textvariable=self.status, wraplength=780).pack(anchor="w", pady=(10, 0))
        self.display_tree()
        self.entry.focus_set()

    def _key_action(self, action):
        try:
            value = int(self.entry.get())
        except ValueError:
            messagebox.showerror("Invalid key", "Please enter a valid integer.", parent=self)
            return
        if action == "insert":
            result = "Inserted" if self.tree.insert(value) else "Already present"
        elif action == "delete":
            result = "Deleted" if self.tree.delete(value) else "Not found"
        else:
            result = "Found" if value in self.tree else "Not found"
        self.status.set(f"{result}: {value}. Keys: {len(self.tree)}.")
        self.display_tree()

    def add_value(self):
        self._key_action("insert")

    def delete_value(self):
        self._key_action("delete")

    def search_value(self):
        self._key_action("search")

    def range_values(self):
        try:
            lower, upper = int(self.lower.get()), int(self.upper.get())
        except ValueError:
            messagebox.showerror("Invalid range", "Enter integer bounds.", parent=self)
            return
        self.status.set(f"Range [{lower}, {upper}]: {self.tree.range_search(lower, upper)}")

    def display_tree(self):
        self.output.configure(state="normal")
        self.output.delete("1.0", tk.END)
        self.output.insert("1.0", format_tree(self.tree.root) + f"\n\nOrdered keys: {list(self.tree)}")
        self.output.configure(state="disabled")

    def export_tree(self):
        path = filedialog.asksaveasfilename(parent=self, defaultextension=".dot",
                                          filetypes=[("Graphviz DOT", "*.dot")])
        if path:
            try:
                export_dot(self.tree, path)
                self.status.set(f"Saved {path}")
            except OSError as error:
                messagebox.showerror("Export failed", str(error), parent=self)


if __name__ == "__main__":
    BPlusTreeGUI().mainloop()
