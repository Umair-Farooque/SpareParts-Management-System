# sale_window.py
import tkinter as tk
from tkinter import ttk, messagebox

class SaleWindow:
    def __init__(self, sales_manager, printer=None, parent=None):
        self.sales_manager = sales_manager
        self.printer = printer
        self.parent = parent

        self.win = tk.Toplevel()
        self.win.title("Sales History")
        self.win.geometry("700x350")
        self.center_window(self.win)

        self.tree = ttk.Treeview(self.win, columns=("ID", "Time", "Part", "Qty", "Total", "Customer", "Invoice"), show="headings")
        for col in self.tree["columns"]:
            self.tree.heading(col, text=col)
            self.tree.column(col, anchor="center")
        self.tree.pack(fill=tk.BOTH, expand=True)

        self.populate_table()

        if self.printer:
            tk.Button(self.win, text="Print Selected Bill", command=self.print_selected).pack(pady=5)

    def center_window(self, win):
        win.update_idletasks()
        width = 700
        height = 350
        if self.parent:
            x = self.parent.winfo_x() + (self.parent.winfo_width() // 2 - width // 2)
            y = self.parent.winfo_y() + (self.parent.winfo_height() // 2 - height // 2)
        else:
            x = win.winfo_screenwidth() // 2 - width // 2
            y = win.winfo_screenheight() // 2 - height // 2
        win.geometry(f"{width}x{height}+{x}+{y}")

    def populate_table(self):
        for i in self.tree.get_children():
            self.tree.delete(i)
        for row in self.sales_manager.get_all_sales():
            # Each row: (id, timestamp, part_name, qty, total_price, customer_name, invoice_no)
            self.tree.insert("", "end", values=row)

    def print_selected(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("No Selection", "Please select a sale to print.")
            return

        sale = self.tree.item(sel[0])["values"]
        sale_id, timestamp, part_name, qty, total, customer_name, invoice = sale

        bill_text = self.printer.generate_bill(customer_name, [{
            "name": part_name,
            "qty": int(qty),
            "total": float(total)
        }], invoice_no=invoice)
        self.printer.print_bill(bill_text)
