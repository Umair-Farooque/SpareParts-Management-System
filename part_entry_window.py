# part_entry_window.py
import tkinter as tk
from tkinter import ttk, messagebox

class PartEntryWindow:
    def __init__(self, inventory):
        self.inv = inventory
        self.win = tk.Toplevel()
        self.win.title("Manage Parts")
        self.win.geometry("700x400")
        self.center_window(self.win)

        self.tree = ttk.Treeview(self.win, columns=("Barcode", "Name", "Company", "Price", "Qty", "UnitType"), show="headings")
        headings = [("Barcode","120"), ("Name","200"), ("Company","120"), ("Price","80"), ("Qty","80"), ("UnitType","80")]
        for col, width in headings:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=int(width))
        self.tree.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        self.load_data()

        form = tk.Frame(self.win)
        form.pack(padx=10, pady=5, fill="x")
        self.fields = {}
        labels = [("Name",""), ("Barcode",""), ("Company",""), ("Price",""), ("Qty",""), ("Litre","")]
        for i, (lbl, _) in enumerate(labels):
            tk.Label(form, text=lbl).grid(row=i, column=0, sticky="w", pady=2)
            entry = tk.Entry(form)
            entry.grid(row=i, column=1, sticky="ew", pady=2)
            self.fields[lbl] = entry
        form.columnconfigure(1, weight=1)

        btn_frame = tk.Frame(self.win)
        btn_frame.pack(pady=8)
        tk.Button(btn_frame, text="Add / Update Part", command=self.add_part).grid(row=0, column=0, padx=5)
        tk.Button(btn_frame, text="Delete Selected", command=self.delete_selected).grid(row=0, column=1, padx=5)
        tk.Button(btn_frame, text="Refresh", command=self.load_data).grid(row=0, column=2, padx=5)

    def center_window(self, win):
        win.update_idletasks()
        width = 700
        height = 400
        x = win.winfo_screenwidth() // 2 - width // 2
        y = win.winfo_screenheight() // 2 - height // 2
        win.geometry(f"{width}x{height}+{x}+{y}")

    def load_data(self):
        for i in self.tree.get_children():
            self.tree.delete(i)
        for row in self.inv.get_all_products():
            # row: (barcode_id, name, company, category, purchase_rate, sale_rate, unit_type, amount)
            barcode_id = row[0]
            name = row[1]
            company = row[2] if row[2] else ""
            price = row[5] if row[5] else 0
            unit_type = row[6] if row[6] else ""
            amount = row[7] if row[7] else 0
            self.tree.insert("", "end", values=(barcode_id, name, company, price, amount, unit_type))

    def add_part(self):
        name = self.fields["Name"].get().strip()
        barcode = self.fields["Barcode"].get().strip()
        company = self.fields["Company"].get().strip()
        price = self.fields["Price"].get().strip()
        qty = self.fields["Qty"].get().strip()
        litre = self.fields["Litre"].get().strip()

        if not name:
            messagebox.showwarning("Missing", "Name is required.")
            return

        # Auto-generate barcode if blank
        if not barcode:
            barcode = self.inv.generate_new_barcode()

        try:
            sale_rate = float(price) if price != "" else 0.0
        except ValueError:
            messagebox.showerror("Invalid", "Price must be a number.")
            return

        try:
            amount = float(qty) if qty != "" else 0.0
        except ValueError:
            messagebox.showerror("Invalid", "Qty must be a number.")
            return

        # Category logic based on litre value
        if litre.strip() == "":
            category_name = "Hardware"
            unit_type = "Quantity"
        else:
            category_name = "Oil"
            unit_type = "Litre"

        self.inv.add_product(
            barcode_id=barcode,
            name=name,
            company=company,
            category_name=category_name,
            purchase_rate=sale_rate,
            sale_rate=sale_rate,
            unit_type=unit_type,
            amount=amount
        )

        self.load_data()
        messagebox.showinfo("Saved", f"Part '{name}' saved/updated successfully.")

    def delete_selected(self):
        sel = self.tree.selection()
        if not sel:
            return
        barcode = self.tree.item(sel[0])["values"][0]
        confirm = messagebox.askyesno("Confirm", f"Delete item {barcode}?")
        if not confirm:
            return
        self.inv.delete_product(barcode)
        self.load_data()
