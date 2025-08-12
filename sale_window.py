import tkinter as tk
from tkinter import ttk, messagebox
import json

class SaleWindow:
    def __init__(self, sales_manager, printer=None, parent=None):
        self.sales_manager = sales_manager
        self.printer = printer
        self.parent = parent

        self.win = tk.Toplevel()
        self.win.title("Sales History")
        self.win.geometry("800x400")
        self.center_window(self.win)

        # Changed columns: Removed "Part" and "Qty" as those are now inside JSON
        self.tree = ttk.Treeview(
            self.win,
            columns=("ID", "Time", "Items", "Total", "Customer", "Invoice"),
            show="headings"
        )
        for col in self.tree["columns"]:
            self.tree.heading(col, text=col)
            self.tree.column(col, anchor="center")
        self.tree.pack(fill=tk.BOTH, expand=True)

        self.populate_table()

        if self.printer:
            tk.Button(self.win, text="Print Selected Bill", command=self.print_selected).pack(pady=5)

    def center_window(self, win):
        win.update_idletasks()
        width = 800
        height = 400
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
            sale_id, timestamp, items_json, total, customer_name, invoice_no = row
            # Parse items JSON and build a short string summary like "item1 x2, item2 x1"
            try:
                items = json.loads(items_json)
                items_str = ", ".join(f"{item['name']} x{item['quantity']}" for item in items)
            except Exception:
                items_str = "Error parsing items"
            self.tree.insert("", "end", values=(sale_id, timestamp, items_str, total, customer_name, invoice_no))

    def print_selected(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("No Selection", "Please select a sale to print.")
            return

        sale = self.tree.item(sel[0])["values"]
        sale_id, timestamp, items_str, total, customer_name, invoice = sale

        # Need to get full items list to print properly:
        # Fetch full sale record again using invoice_no (to get JSON)
        sale_record = self.sales_manager.get_sale_by_invoice(invoice)
        if not sale_record:
            messagebox.showerror("Error", "Could not retrieve sale details.")
            return

        _, _, items_json, _, _, _ = sale_record
        try:
            items = json.loads(items_json)
        except Exception:
            messagebox.showerror("Error", "Failed to parse sale items.")
            return

        bill_text = self.printer.generate_bill(customer_name, items, invoice_no=invoice)
        self.printer.print_bill(bill_text)
