import tkinter as tk
from tkinter import messagebox
from bplustree import Bplustree
from utils import print_tree
import graphviz

class BPlusTreeGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("B+ Tree GUI")
        self.geometry("400x300")
        self.configure(bg="#f0f0f0")

        self.tree = Bplustree(4)

        self.entry_label = tk.Label(self, text="Enter Value:", bg="#f0f0f0", fg="#333")
        self.entry_label.pack(pady=5)
        self.entry = tk.Entry(self, width=20, bd=2)
        self.entry.pack()

        self.add_button = tk.Button(self, text="Add Value", command=self.add_value, bg="#4caf50", fg="#fff")
        self.add_button.pack(pady=5)

        self.delete_button = tk.Button(self, text="Delete Value", command=self.delete_value, bg="#f44336", fg="#fff")
        self.delete_button.pack(pady=5)

        self.display_button = tk.Button(self, text="Display Tree", command=self.display_tree, bg="#2196f3", fg="#fff")
        self.display_button.pack(pady=5)

    def add_value(self):
        value = self.entry.get()
        if value.strip() == "":
            messagebox.showerror("Error", "Please enter a value.")
            return
        try:
            value = int(value)
            self.tree.insert(value)
            messagebox.showinfo("Success", f"Value {value} has been added to the tree.")
            self.entry.delete(0, tk.END)
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid integer.")

    def delete_value(self):
        value = self.entry.get()
        if value.strip() == "":
            messagebox.showerror("Error", "Please enter a value.")
            return
        try:
            value = int(value)
            self.tree.delete(value)
            messagebox.showinfo("Success", f"Value {value} has been deleted from the tree.")
            self.entry.delete(0, tk.END)
        except ValueError:
            messagebox.showerror("Error", "Please enter a valid integer.")

    def display_tree(self):
        dot = graphviz.Digraph()
        self._traverse_tree(self.tree.root, dot)
        dot.render('bplus_tree', format='png', cleanup=True)
        messagebox.showinfo("Info", "Tree visualization saved as bplus_tree.png")

    def _traverse_tree(self, node, dot):
        if node is not None:
            if node.t == 'node':
                dot.node(str(node), label=str(node.keys))
                for child in node.children:
                    self._traverse_tree(child, dot)
                    dot.edge(str(node), str(child))
            else:  # Handle leaf nodes
                dot.node(str(node), label="|".join(map(str, node.keys)))

if __name__ == "__main__":
    app = BPlusTreeGUI()
    app.mainloop()
