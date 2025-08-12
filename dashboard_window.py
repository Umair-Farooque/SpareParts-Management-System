# dashboard_window.py
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
        self.win.geometry("800x500")

        title_label = tk.Label(self.win, text="Al-Hafiz Autos", font=("Arial", 20, "bold"), fg="#1a237e")
        title_label.pack(pady=10)

        self.menu_bar = tk.Menu(self.win)
        inventory_menu = tk.Menu(self.menu_bar, tearoff=0)
        inventory_menu.add_command(label="Add Part", command=self.add_part)
        inventory_menu.add_command(label="Delete Part", command=self.delete_part)
        inventory_menu.add_command(label="Update Part", command=self.update_part)
        inventory_menu.add_command(label="Refresh", command=self.refresh_table)
        self.menu_bar.add_cascade(label="Inventory", menu=inventory_menu)
        self.menu_bar.add_command(label="View Sales", command=self.view_sales)
        self.menu_bar.add_command(label="Search Invoice", command=self.search_invoice)
        self.menu_bar.add_command(label="Logout", command=self.logout)
        self.win.config(menu=self.menu_bar)

        tk.Button(self.win, text="Sell", command=lambda: SellWindow(self.inventory, self.sales, printer=self.printer, parent=self.win)).pack()

        # Search bar frame
        search_frame = tk.Frame(self.win)
        search_frame.pack(pady=5)
        tk.Label(search_frame, text="Search by Name:").pack(side=tk.LEFT, padx=(0, 5))

        self.search_var = tk.StringVar()
        self.search_var.trace_add("write", self.on_search)  # Calls on_search whenever text changes

        self.search_entry = tk.Entry(search_frame, textvariable=self.search_var)
        self.search_entry.pack(side=tk.LEFT)

        self.tree = ttk.Treeview(self.win, columns=("ID", "Name", "Company", "Purchase Rate", "Price", "Qty"), show="headings")
        for col in ("ID", "Name", "Company", "Purchase Rate", "Price", "Qty"):
            self.tree.heading(col, text=col)
            self.tree.column(col, anchor="center", width=120)
        self.tree.pack(fill=tk.BOTH, expand=True)

        tk.Button(self.win, text="Sell Selected", command=self.sell_selected).pack(pady=5)
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
        for row in self.inventory.get_all_parts():
            self.tree.insert("", "end", values=row)

    def on_search(self, *args):
        search_text = self.search_var.get().lower().strip()
        self.tree.delete(*self.tree.get_children())

        for row in self.inventory.get_all_parts():
            # row format: (id, name, company, price, qty)
            if search_text in row[1].lower():
                self.tree.insert("", "end", values=row)

    def get_selected_part_id(self):
        sel = self.tree.selection()
        if not sel:
            messagebox.showwarning("No Selection", "Select a part from the table.")
            return None
        return self.tree.item(sel[0])["values"][0]

    def add_part(self):
        if hasattr(self, 'add_window') and self.add_window.winfo_exists():
            self.add_window.lift()
            return

        self.add_window = tk.Toplevel(self.win)
        self.add_window.title("Add Part")
        self.add_window.geometry("400x250")
        self.center_popup(self.add_window)

        labels = ["Name", "Part No", "Price", "Quantity"]
        entries = {}

        for label in labels:
            tk.Label(self.add_window, text=label).pack()
            entries[label] = tk.Entry(self.add_window)
            entries[label].pack()

        def submit():
            try:
                self.inventory.add_part(
                    entries["Name"].get(),
                    entries["Part No"].get(),
                    float(entries["Price"].get()),
                    int(entries["Quantity"].get())
                )
                self.refresh_table()
                self.add_window.destroy()
            except Exception as e:
                messagebox.showerror("Error", f"Invalid input: {e}")

        tk.Button(self.add_window, text="Add", command=submit).pack(pady=5)

    def delete_part(self):
        part_id = self.get_selected_part_id()
        if part_id:
            self.inventory.delete_part(part_id)
            self.refresh_table()

    def update_part(self):
        part_id = self.get_selected_part_id()
        if not part_id:
            return

        for row in self.inventory.get_all_parts():
            if row[0] == part_id:
                part_data = row
                break
        else:
            messagebox.showerror("Error", "Part not found.")
            return

        update_window = tk.Toplevel(self.win)
        update_window.title("Update Part")
        update_window.geometry("400x250")
        self.center_popup(update_window)

        labels = ["Name", "Part No", "Price", "Qty"]
        entries = {}

        for i, label in enumerate(labels):
            tk.Label(update_window, text=label).pack()
            entries[label] = tk.Entry(update_window)
            entries[label].insert(0, part_data[i + 1])
            entries[label].pack()

        def submit():
            try:
                self.inventory.delete_part(part_id)
                self.inventory.add_part(
                    entries["Name"].get(),
                    entries["Part No"].get(),
                    float(entries["Price"].get()),
                    int(entries["Qty"].get())
                )
                self.refresh_table()
                update_window.destroy()
            except Exception as e:
                messagebox.showerror("Error", f"Invalid input: {e}")

        tk.Button(update_window, text="Update", command=submit).pack(pady=5)

    def sell_selected(self):
        part_id = self.get_selected_part_id()
        if not part_id:
            return

        for row in self.inventory.get_all_parts():
            if row[0] == part_id:
                part_data = row
                break

        sell_win = tk.Toplevel(self.win)
        sell_win.title("Sell Part")
        sell_win.geometry("400x250")
        self.center_popup(sell_win)

        tk.Label(sell_win, text="Customer Name").pack()
        entry_cust = tk.Entry(sell_win)
        entry_cust.pack()

        tk.Label(sell_win, text="Quantity").pack()
        entry_qty = tk.Entry(sell_win)
        entry_qty.pack()

        def submit():
            try:
                qty = int(entry_qty.get())
                customer = entry_cust.get()
                total = qty * float(part_data[3])
                if qty > part_data[4]:
                    messagebox.showerror("Error", "Not enough stock")
                    return
                invoice = self.sales.record_sale(part_id, qty, total, customer)
                self.inventory.update_qty(part_id, -qty)
                self.refresh_table()
                bill_text = self.printer.generate_bill(
                    customer, [{"name": part_data[1], "qty": qty, "total": total}],
                    invoice_no=invoice
                )
                self.printer.print_bill(bill_text)
                sell_win.destroy()
            except Exception as e:
                messagebox.showerror("Error", str(e))

        tk.Button(sell_win, text="Sell", command=submit).pack(pady=5)

    def view_sales(self):
        SaleWindow(self.sales, self.printer, parent=self.win)

    def search_invoice(self):
        InvoiceSearchWindow(self.sales, self.printer, parent=self.win)

    def logout(self):
        self.win.destroy()
