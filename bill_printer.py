import tkinter as tk
import tempfile
import os
import datetime

class BillPrinter:
    def generate_bill(self, customer_name, items, invoice_no=None):
        lines = []
        lines.append("      AL-HAFIZ AUTOS")
        lines.append("============================")
        if invoice_no:
            lines.append(f"Invoice #: {invoice_no}")
        lines.append(f"Customer: {customer_name}")
        lines.append("----------------------------")
        total = 0
        for item in items:
            lines.append(f"{item['name']} x{item['qty']} = Rs.{item['total']}")
            total += item['total']
        lines.append("----------------------------")
        lines.append(f"Total: Rs.{total}")
        lines.append(f"Date: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        lines.append("============================")
        return "\n".join(lines)

    def print_bill(self, text):
        with open("bill.txt", "w") as f:
            f.write(text)
        # os.startfile("bill.txt", "print")  # Uncomment when ready to auto print

