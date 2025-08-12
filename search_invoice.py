# invoice_search_window.py
import tkinter as tk
from tkinter import messagebox

class InvoiceSearchWindow:
    def __init__(self, sales_manager, printer=None, parent=None):
        self.sales_manager = sales_manager
        self.printer = printer

        self.win = tk.Toplevel(parent) if parent else tk.Toplevel()
        self.win.title("Search Invoice")
        self.win.geometry("400x180")
        self.center_window(self.win)

        tk.Label(self.win, text="Enter Invoice Number").pack(pady=10)
        self.entry = tk.Entry(self.win)
        self.entry.pack(padx=10, fill="x")

        tk.Button(self.win, text="Search", command=self.search).pack(pady=10)

    def center_window(self, win):
        win.update_idletasks()
        width = 400
        height = 180
        x = win.winfo_screenwidth() // 2 - width // 2
        y = win.winfo_screenheight() // 2 - height // 2
        win.geometry(f"{width}x{height}+{x}+{y}")

    def search(self):
        invoice_no = self.entry.get().strip()
        result = self.sales_manager.get_sale_by_invoice(invoice_no)
        if not result:
            messagebox.showerror("Not Found", "No sale found with this invoice number.")
            return

        sale_id, timestamp, part_name, qty, total, customer_name, invoice = result
        bill_text = self.printer.generate_bill(customer_name, [{
            "name": part_name,
            "qty": qty,
            "total": total
        }], invoice_no=invoice)
        self.printer.print_bill(bill_text)
