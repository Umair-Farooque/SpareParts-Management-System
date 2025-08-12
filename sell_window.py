import tkinter as tk
from tkinter import ttk, messagebox
import json
import time

class SellWindow:
    def __init__(self, inventory_manager, sales_manager, printer=None, parent=None):
        self.inventory_manager = inventory_manager
        self.sales_manager = sales_manager
        self.printer = printer
        self.parent = parent
        self.cart = {}  # barcode → {"name": str, "price": float, "qty": int}

        self.win = tk.Toplevel()
        self.win.title("Sell Items (Barcode Mode)")
        self.win.geometry("700x450")
        self.center_window(self.win)

        # Barcode entry
        tk.Label(self.win, text="Scan Barcode:").pack(pady=5)
        self.barcode_entry = tk.Entry(self.win, font=("Arial", 14))
        self.barcode_entry.pack(pady=5)
        self.barcode_entry.bind("<Return>", self.add_barcode)
        self.barcode_entry.focus()

        # Cart table
        self.tree = ttk.Treeview(self.win, columns=("Name", "Qty", "Price", "Subtotal"), show="headings")
        for col in self.tree["columns"]:
            self.tree.heading(col, text=col)
            self.tree.column(col, anchor="center", width=120)
        self.tree.pack(fill=tk.BOTH, expand=True, pady=5)

        # Remove button
        tk.Button(self.win, text="Remove Selected Item", command=self.remove_selected_item, bg="orange").pack(pady=5)

        # Total price
        self.total_label = tk.Label(self.win, text="Total: 0.00", font=("Arial", 14, "bold"))
        self.total_label.pack(pady=5)

        # Buttons
        btn_frame = tk.Frame(self.win)
        btn_frame.pack(pady=5)
        tk.Button(btn_frame, text="Confirm Sale", command=self.confirm_sale, bg="green", fg="white").pack(side=tk.LEFT, padx=5)
        tk.Button(btn_frame, text="Cancel", command=self.win.destroy, bg="red", fg="white").pack(side=tk.LEFT, padx=5)

    def center_window(self, win):
        win.update_idletasks()
        width = 700
        height = 450
        if self.parent:
            x = self.parent.winfo_x() + (self.parent.winfo_width() // 2 - width // 2)
            y = self.parent.winfo_y() + (self.parent.winfo_height() // 2 - height // 2)
        else:
            x = win.winfo_screenwidth() // 2 - width // 2
            y = win.winfo_screenheight() // 2 - height // 2
        win.geometry(f"{width}x{height}+{x}+{y}")

    def add_barcode(self, event=None):
        barcode = self.barcode_entry.get().strip()
        self.barcode_entry.delete(0, tk.END)
        if not barcode:
            return

        product = self.inventory_manager.get_product_by_barcode(barcode)
        if not product:
            messagebox.showerror("Not Found", f"No product found for barcode: {barcode}")
            return

        name, price = product["name"], float(product["price"])
        if barcode in self.cart:
            self.cart[barcode]["qty"] += 1
        else:
            self.cart[barcode] = {"name": name, "price": price, "qty": 1}

        self.update_cart_display()

    def update_cart_display(self):
        for i in self.tree.get_children():
            self.tree.delete(i)

        total_price = 0
        for barcode, item in self.cart.items():
            subtotal = item["price"] * item["qty"]
            total_price += subtotal
            self.tree.insert("", "end", iid=barcode, values=(item["name"], item["qty"], f"{item['price']:.2f}", f"{subtotal:.2f}"))

        self.total_label.config(text=f"Total: {total_price:.2f}")

    def remove_selected_item(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("No Selection", "Please select an item to remove.")
            return
        barcode = selected[0]
        if barcode in self.cart:
            del self.cart[barcode]
        self.update_cart_display()

    def confirm_sale(self):
        if not self.cart:
            messagebox.showwarning("Empty Cart", "No items in cart.")
            return

        invoice_no = f"INV-{int(time.time())}"
        items_list = [
            {"name": item["name"], "qty": item["qty"], "price": item["price"], "total": item["price"] * item["qty"]}
            for item in self.cart.values()
        ]
        total_amount = sum(item["total"] for item in items_list)

        # Store in DB as single record
        self.sales_manager.add_sale(
            timestamp=time.strftime("%Y-%m-%d %H:%M:%S"),
            items_json=json.dumps(items_list),
            total_price=total_amount,
            customer_name="",
            invoice_no=invoice_no
        )

        # Reduce stock
        for barcode, item in self.cart.items():
            self.inventory_manager.reduce_stock(barcode, item["qty"])

        # Print bill
        if self.printer:
            bill_text = self.printer.generate_bill("", items_list, invoice_no=invoice_no)
            self.printer.print_bill(bill_text)

        messagebox.showinfo("Sale Complete", f"Sale recorded with Invoice No: {invoice_no}")
        self.win.destroy()
