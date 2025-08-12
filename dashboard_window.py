import tkinter as tk
from tkinter import ttk, messagebox
from sale_window import SaleWindow
from search_invoice import InvoiceSearchWindow
from sell_window import SellWindow


class DashboardWindow:
    def __init__(self, auth, inventory, sales, printer, user):
        self.auth = auth
        self.inventory = inventory
        self.sales = sales
        self.printer = printer
        self.user = user

        self.win = tk.Tk()
        self.win.title("Al-Hafiz Autos - Dashboard")
        self.win.geometry("1000x650")
        self.win.configure(bg="#f5f7fa")
        self.win.state('zoomed')

        # --- Menu Bar ---
        self.menu_bar = tk.Menu(self.win)

        inventory_menu = tk.Menu(self.menu_bar, tearoff=0)
        inventory_menu.add_command(label="Add Part", command=self.add_part)
        inventory_menu.add_command(label="Update Part", command=self.update_part)
        inventory_menu.add_command(label="Delete Part", command=self.delete_part)
        inventory_menu.add_separator()
        inventory_menu.add_command(label="Refresh", command=self.refresh_table)

        self.menu_bar.add_cascade(label="Inventory", menu=inventory_menu)
        self.menu_bar.add_command(label="View Sales", command=self.view_sales)
        self.menu_bar.add_command(label="Search Invoice", command=self.search_invoice)
        self.menu_bar.add_command(label="Logout", command=self.logout)

        self.win.config(menu=self.menu_bar)

        # Styles
        style = ttk.Style(self.win)
        style.theme_use('clam')
        style.configure("Treeview.Heading", font=("Segoe UI", 11, "bold"), foreground="#1a237e")
        style.configure("Treeview", font=("Segoe UI", 10), rowheight=25)
        style.configure("TButton", font=("Segoe UI", 10, "bold"), padding=6)
        style.map('TButton',
                  background=[('active', '#1a237e')],
                  foreground=[('active', 'white')])

        # Title Frame
        title_frame = tk.Frame(self.win, bg="#f5f7fa")
        title_frame.pack(pady=15)

        title_label = tk.Label(
            title_frame, text="Al-Hafiz Autos",
            font=("Segoe UI", 24, "bold"),
            fg="#1a237e",
            bg="#f5f7fa"
        )
        title_label.pack()

        # Search Frame
        search_frame = tk.Frame(self.win, bg="#f5f7fa")
        search_frame.pack(pady=10, fill=tk.X, padx=20)

        search_label = tk.Label(search_frame, text="Search by Name:", font=("Segoe UI", 11), bg="#f5f7fa")
        search_label.pack(side=tk.LEFT, padx=(0, 8))

        self.search_var = tk.StringVar()
        self.search_var.trace_add("write", self.on_search)

        self.search_entry = ttk.Entry(search_frame, textvariable=self.search_var, width=35)
        self.search_entry.pack(side=tk.LEFT, padx=(0, 20))

        # Sell Button Frame
        sell_btn = ttk.Button(search_frame, text="Sell", command=lambda: SellWindow(self.inventory, self.sales, printer=self.printer, parent=self.win))
        sell_btn.pack(side=tk.RIGHT)

        # Treeview Frame
        tree_frame = tk.Frame(self.win)
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        # Columns without Barcode ID
        self.tree = ttk.Treeview(tree_frame, columns=("Name", "Company", "Purchase Rate", "Sale Rate", "Quantity"),
                                 show="headings", selectmode="browse")
        self.tree.heading("Name", text="Name")
        self.tree.heading("Company", text="Company")
        self.tree.heading("Purchase Rate", text="Purchase Rate")
        self.tree.heading("Sale Rate", text="Sale Rate")
        self.tree.heading("Quantity", text="Quantity")

        self.tree.column("Name", width=220, anchor="w")
        self.tree.column("Company", width=150, anchor="w")
        self.tree.column("Purchase Rate", width=100, anchor="center")
        self.tree.column("Sale Rate", width=100, anchor="center")
        self.tree.column("Quantity", width=80, anchor="center")

        vsb = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=vsb.set)
        vsb.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.pack(fill=tk.BOTH, expand=True)

        self.refresh_table()

        self.win.mainloop()

    def center_popup(self, popup):
        popup.update_idletasks()
        w = popup.winfo_width()
        h = popup.winfo_height()
        x = self.win.winfo_x() + (self.win.winfo_width() // 2 - w // 2)
        y = self.win.winfo_y() + (self.win.winfo_height() // 2 - h // 2)
        popup.geometry(f"{w}x{h}+{x}+{y}")

    def refresh_table(self):
        for i in self.tree.get_children():
            self.tree.delete(i)

        all_products = self.inventory.get_all_products()
        for prod in all_products:
            # prod = (barcode_id, item_name, company, purchase_rate, sale_rate, amount)
            self.tree.insert("", "end", values=prod[1:])  # skip barcode_id

    def on_search(self, *args):
        search_text = self.search_var.get().lower().strip()
        self.tree.delete(*self.tree.get_children())

        all_products = self.inventory.get_all_products()
        for prod in all_products:
            if search_text in prod[1].lower():  # item_name at index 1
                self.tree.insert("", "end", values=prod[1:])

    def get_selected_part_barcode(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("No Selection", "Select a part from the table.")
            return None

        selected_values = self.tree.item(sel[0])["values"]
        selected_name = selected_values[0]
        selected_company = selected_values[1]

        all_products = self.inventory.get_all_products()
        for prod in all_products:
            if prod[1] == selected_name and prod[2] == selected_company:
                return prod[0]

        messagebox.showerror("Error", "Could not find product barcode.")
        return None

    def add_part(self):
        if hasattr(self, 'add_window') and self.add_window.winfo_exists():
            self.add_window.lift()
            return

        self.add_window = tk.Toplevel(self.win)
        self.add_window.title("Add Part")
        self.add_window.geometry("400x350")
        self.center_popup(self.add_window)

        # Create entry fields
        entries = {}  # Initialize the entries dictionary
        
        tk.Label(self.add_window, text="Name").pack(pady=3)
        entries["Name"] = ttk.Entry(self.add_window)
        entries["Name"].pack()
        
        tk.Label(self.add_window, text="Company").pack(pady=3)
        entries["Company"] = ttk.Entry(self.add_window)
        entries["Company"].pack()
        
        # Category dropdown (1 for Quantity, 2 for Litres)
        tk.Label(self.add_window, text="Category").pack(pady=3)
        category_var = tk.StringVar(value="1")  # Default to Quantity
        category_menu = ttk.OptionMenu(self.add_window, category_var, "1", "1 - Quantity", "2 - Litres")
        category_menu.pack()
        
        tk.Label(self.add_window, text="Purchase Rate").pack(pady=3)
        entries["Purchase Rate"] = ttk.Entry(self.add_window)
        entries["Purchase Rate"].pack()
        
        tk.Label(self.add_window, text="Sale Rate").pack(pady=3)
        entries["Sale Rate"] = ttk.Entry(self.add_window)
        entries["Sale Rate"].pack()
        
        tk.Label(self.add_window, text="Quantity").pack(pady=3)
        entries["Quantity"] = ttk.Entry(self.add_window)
        entries["Quantity"].pack()

        def submit():
            try:
                self.inventory.add_product(
                    name=entries["Name"].get(),
                    company=entries["Company"].get(),
                    category_id=int(category_var.get().split(" ")[0]),  # Get the number part
                    purchase_rate=float(entries["Purchase Rate"].get()),
                    sale_rate=float(entries["Sale Rate"].get()),
                    amount=float(entries["Quantity"].get())
                )
                self.refresh_table()
                self.add_window.destroy()
            except Exception as e:
                messagebox.showerror("Error", f"Invalid input or {e}")

        ttk.Button(self.add_window, text="Add", command=submit).pack(pady=10)

    def delete_part(self):
        barcode_id = self.get_selected_part_barcode()
        if barcode_id:
            confirm = messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this part?")
            if confirm:
                self.inventory.delete_product(barcode_id)
                self.refresh_table()

    def update_part(self):
        barcode_id = self.get_selected_part_barcode()
        if not barcode_id:
            return

        part_data = self.inventory.get_product(barcode_id)
        if not part_data:
            messagebox.showerror("Error", "Part not found.")
            return

        update_window = tk.Toplevel(self.win)
        update_window.title("Update Part")
        update_window.geometry("400x350")
        self.center_popup(update_window)

        # Create entry fields
        entries = {}
        
        # Name
        tk.Label(update_window, text="Name").pack(pady=3)
        entries["Name"] = ttk.Entry(update_window)
        entries["Name"].insert(0, part_data[1])  # name at index 1
        entries["Name"].pack()
        
        # Company
        tk.Label(update_window, text="Company").pack(pady=3)
        entries["Company"] = ttk.Entry(update_window)
        entries["Company"].insert(0, part_data[2])  # company at index 2
        entries["Company"].pack()
        
        # Category dropdown (1 for Quantity, 2 for Litres)
        tk.Label(update_window, text="Category").pack(pady=3)
        category_var = tk.StringVar(value=str(part_data[3]))  # category_id at index 3
        category_menu = ttk.OptionMenu(update_window, category_var, "1", "1 - Quantity", "2 - Litres")
        category_menu.pack()
        
        # Purchase Rate
        tk.Label(update_window, text="Purchase Rate").pack(pady=3)
        entries["Purchase Rate"] = ttk.Entry(update_window)
        entries["Purchase Rate"].insert(0, part_data[4])  # purchase_rate at index 4
        entries["Purchase Rate"].pack()
        
        # Sale Rate
        tk.Label(update_window, text="Sale Rate").pack(pady=3)
        entries["Sale Rate"] = ttk.Entry(update_window)
        entries["Sale Rate"].insert(0, part_data[5])  # sale_rate at index 5
        entries["Sale Rate"].pack()
        
        # Quantity
        tk.Label(update_window, text="Quantity").pack(pady=3)
        entries["Quantity"] = ttk.Entry(update_window)
        entries["Quantity"].insert(0, part_data[7])  # amount at index 7
        entries["Quantity"].pack()

        def submit():
            try:
                self.inventory.add_product(
                    barcode_id=barcode_id,
                    name=entries["Name"].get(),
                    company=entries["Company"].get(),
                    category_id=int(category_var.get().split(" ")[0]),  # Get the number part
                    purchase_rate=float(entries["Purchase Rate"].get()),
                    sale_rate=float(entries["Sale Rate"].get()),
                    amount=float(entries["Quantity"].get())
                )
                self.refresh_table()
                update_window.destroy()
            except Exception as e:
                messagebox.showerror("Error", f"Invalid input or {e}")

        ttk.Button(update_window, text="Update", command=submit).pack(pady=10)

    def sell_selected(self):
        barcode_id = self.get_selected_part_barcode()
        if not barcode_id:
            return

        part_data = self.inventory.get_product(barcode_id)
        if not part_data:
            messagebox.showerror("Error", "Part not found.")
            return

        sell_win = tk.Toplevel(self.win)
        sell_win.title("Sell Part")
        sell_win.geometry("400x250")
        self.center_popup(sell_win)

        tk.Label(sell_win, text="Customer Name").pack(pady=5)
        entry_cust = ttk.Entry(sell_win)
        entry_cust.pack()

        tk.Label(sell_win, text="Quantity").pack(pady=5)
        entry_qty = ttk.Entry(sell_win)
        entry_qty.pack()

        def submit():
            try:
                qty = float(entry_qty.get())
                customer = entry_cust.get()
                price_per_unit = part_data[5]  # sale_rate
                stock_qty = part_data[7]       # quantity

                total = qty * price_per_unit
                if qty > stock_qty:
                    messagebox.showerror("Error", "Not enough stock")
                    return

                invoice = self.sales.record_sale(barcode_id, qty, total, customer)
                self.inventory.update_stock(barcode_id, -qty)
                self.refresh_table()
                bill_text = self.printer.generate_bill(
                    customer, [{"name": part_data[1], "qty": qty, "total": total}],
                    invoice_no=invoice
                )
                self.printer.print_bill(bill_text)
                sell_win.destroy()
            except Exception as e:
                messagebox.showerror("Error", str(e))

        ttk.Button(sell_win, text="Sell", command=submit).pack(pady=15)

    def view_sales(self):
        SaleWindow(self.sales, self.printer, parent=self.win)

    def search_invoice(self):
        InvoiceSearchWindow(self.sales, self.printer, parent=self.win)

    def logout(self):
        self.win.destroy()
