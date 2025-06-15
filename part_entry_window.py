import tkinter as tk
from tkinter import ttk

class PartEntryWindow:
    def __init__(self, inventory):
        self.inv = inventory
        self.win = tk.Toplevel()
        self.win.title("Manage Parts")

        self.tree = ttk.Treeview(self.win, columns=("ID", "Name", "Part No", "Price", "Qty"), show="headings")
        for col in self.tree["columns"]:
            self.tree.heading(col, text=col)
        self.tree.pack()

        self.load_data()

        form = tk.Frame(self.win)
        form.pack()
        self.fields = {}
        for lbl in ["Name", "Part No", "Price", "Qty"]:
            tk.Label(form, text=lbl).grid()
            self.fields[lbl] = tk.Entry(form)
            self.fields[lbl].grid()

        tk.Button(form, text="Add Part", command=self.add_part).grid(columnspan=2)

        tk.Button(form, text="Delete Selected", command=self.delete_selected).grid(columnspan=2)

    def load_data(self):
        for i in self.tree.get_children():
            self.tree.delete(i)
        for row in self.inv.get_all_parts():
            self.tree.insert("", "end", values=row)

    def add_part(self):
        args = [self.fields[f].get() for f in self.fields]
        self.inv.add_part(*args)
        self.load_data()

    def delete_selected(self):
        sel = self.tree.selection()
        if not sel: return
        part_id = self.tree.item(sel[0])["values"][0]
        self.inv.delete_part(part_id)
        self.load_data()
