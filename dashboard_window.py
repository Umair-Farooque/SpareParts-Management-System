from PyQt6.QtWidgets import (
    QWidget, QMainWindow, QLabel, QLineEdit, QPushButton, QVBoxLayout, QHBoxLayout,
    QTableWidget, QTableWidgetItem, QMessageBox, QComboBox, QDialog, QHeaderView
)
from PyQt6.QtGui import QAction
from PyQt6.QtCore import Qt
from search_invoice import InvoiceSearchWindow
from sale_window import SaleWindow 


class DashboardWindow(QMainWindow):
    def __init__(self, auth, inventory, sales, printer, user):
        super().__init__()
        self.auth = auth
        self.inventory = inventory
        self.sales = sales
        self.printer = printer
        self.user = user

        self.setWindowTitle("Al-Hafiz Autos - Dashboard")
        self.resize(1000, 650)

        self._setup_menu()
        self._setup_ui()
        self.refresh_table()

    def _setup_menu(self):
        menubar = self.menuBar()

        inventory_menu = menubar.addMenu("Inventory")

        add_part_action = QAction("Add Part", self)
        add_part_action.triggered.connect(self.add_part)
        inventory_menu.addAction(add_part_action)

        update_part_action = QAction("Update Part", self)
        update_part_action.triggered.connect(self.update_part)
        inventory_menu.addAction(update_part_action)

        delete_part_action = QAction("Delete Part", self)
        delete_part_action.triggered.connect(self.delete_part)
        inventory_menu.addAction(delete_part_action)

        inventory_menu.addSeparator()

        refresh_action = QAction("Refresh", self)
        refresh_action.triggered.connect(self.refresh_table)
        inventory_menu.addAction(refresh_action)

        view_sales_action = QAction("View Sales", self)
        view_sales_action.triggered.connect(self.view_sales)
        menubar.addAction(view_sales_action)

        search_invoice_action = QAction("Search Invoice", self)
        search_invoice_action.triggered.connect(self.search_invoice)
        menubar.addAction(search_invoice_action)

        logout_action = QAction("Logout", self)
        logout_action.triggered.connect(self.logout)
        menubar.addAction(logout_action)

    def _setup_ui(self):
        main_widget = QWidget()
        self.setCentralWidget(main_widget)

        layout = QVBoxLayout(main_widget)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        title_label = QLabel("Al-Hafiz Autos")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setStyleSheet("font-size: 24px; font-weight: bold; color: #1a237e;")
        layout.addWidget(title_label)

        # Search bar and Sell button row
        search_layout = QHBoxLayout()
        layout.addLayout(search_layout)

        search_label = QLabel("Search by Name:")
        search_label.setStyleSheet("font-size: 14px;")
        search_layout.addWidget(search_label)

        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("Enter part name to search")
        self.search_edit.textChanged.connect(self.on_search)
        search_layout.addWidget(self.search_edit)

        sell_btn = QPushButton("Sell")
        sell_btn.clicked.connect(self.sell_selected)
        search_layout.addWidget(sell_btn)

        # Table widget for inventory
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["Name", "Company", "Purchase Rate", "Sale Rate", "Quantity"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setSelectionBehavior(self.table.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(self.table.SelectionMode.SingleSelection)
        layout.addWidget(self.table)

    def refresh_table(self):
        all_products = self.inventory.get_all_products()
        self.table.setRowCount(0)
        search_text = self.search_edit.text().lower().strip()

        for prod in all_products:
            # prod = (barcode_id, item_name, company, purchase_rate, sale_rate, amount)
            if search_text in prod[1].lower():
                row = self.table.rowCount()
                self.table.insertRow(row)
                self.table.setItem(row, 0, QTableWidgetItem(prod[1]))
                self.table.setItem(row, 1, QTableWidgetItem(prod[2]))
                self.table.setItem(row, 2, QTableWidgetItem(str(prod[3])))
                self.table.setItem(row, 3, QTableWidgetItem(str(prod[4])))
                self.table.setItem(row, 4, QTableWidgetItem(str(prod[5])))

    def on_search(self, text):
        self.refresh_table()

    def get_selected_part_barcode(self):
        selected_items = self.table.selectedItems()
        if not selected_items:
            QMessageBox.warning(self, "No Selection", "Select a part from the table.")
            return None
        selected_name = selected_items[0].text()
        selected_company = selected_items[1].text()

        all_products = self.inventory.get_all_products()
        for prod in all_products:
            if prod[1] == selected_name and prod[2] == selected_company:
                return prod[0]
        QMessageBox.critical(self, "Error", "Could not find product barcode.")
        return None

    def add_part(self):
        dialog = PartDialog(self, "Add Part")
        if dialog.exec():
            data = dialog.get_data()
            try:
                self.inventory.add_product(
                    name=data["Name"],
                    company=data["Company"],
                    category_id=int(data["Category"].split()[0]),
                    purchase_rate=float(data["Purchase Rate"]),
                    sale_rate=float(data["Sale Rate"]),
                    amount=float(data["Quantity"])
                )
                self.refresh_table()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Invalid input or {e}")

    def delete_part(self):
        barcode_id = self.get_selected_part_barcode()
        if barcode_id:
            confirm = QMessageBox.question(self, "Confirm Delete", "Are you sure you want to delete this part?")
            if confirm == QMessageBox.StandardButton.Yes:
                self.inventory.delete_product(barcode_id)
                self.refresh_table()

    def update_part(self):
        barcode_id = self.get_selected_part_barcode()
        if not barcode_id:
            return

        part_data = self.inventory.get_product(barcode_id)
        if not part_data:
            QMessageBox.critical(self, "Error", "Part not found.")
            return

        dialog = PartDialog(self, "Update Part", part_data)
        if dialog.exec():
            data = dialog.get_data()
            try:
                self.inventory.add_product(
                    barcode_id=barcode_id,
                    name=data["Name"],
                    company=data["Company"],
                    category_id=int(data["Category"].split()[0]),
                    purchase_rate=float(data["Purchase Rate"]),
                    sale_rate=float(data["Sale Rate"]),
                    amount=float(data["Quantity"])
                )
                self.refresh_table()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Invalid input or {e}")

    def sell_selected(self):
        barcode_id = self.get_selected_part_barcode()
        if not barcode_id:
            return

        part_data = self.inventory.get_product(barcode_id)
        if not part_data:
            QMessageBox.critical(self, "Error", "Part not found.")
            return

        dialog = SellDialog(self, part_data)
        if dialog.exec():
            customer, qty = dialog.get_data()
            price_per_unit = part_data[5]  # sale_rate
            stock_qty = part_data[7]       # quantity
            total = qty * price_per_unit
            if qty > stock_qty:
                QMessageBox.critical(self, "Error", "Not enough stock")
                return

            invoice = self.sales.record_sale(barcode_id, qty, total, customer)
            self.inventory.update_stock(barcode_id, -qty)
            self.refresh_table()
            bill_text = self.printer.generate_bill(
                customer, [{"name": part_data[1], "qty": qty, "total": total}],
                invoice_no=invoice
            )
            self.printer.print_bill(bill_text)

    def view_sales(self):
        dialog = SaleWindow(self.sales, self.printer, parent=self)
        dialog.exec()  # Use exec() to open as a modal dialog


    def search_invoice(self):
        self.invoice_search_dialog = InvoiceSearchWindow(self.sales, self.printer, parent=self)
        self.invoice_search_dialog.exec()  # open modal dialog

    def logout(self):
        self.close()


class PartDialog(QDialog):
    def __init__(self, parent, title, part_data=None):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.setFixedSize(400, 350)

        layout = QVBoxLayout(self)

        # Name
        layout.addWidget(QLabel("Name"))
        self.name_edit = QLineEdit()
        layout.addWidget(self.name_edit)

        # Company
        layout.addWidget(QLabel("Company"))
        self.company_edit = QLineEdit()
        layout.addWidget(self.company_edit)

        # Category dropdown
        layout.addWidget(QLabel("Category"))
        self.category_combo = QComboBox()
        self.category_combo.addItems(["1 - Quantity", "2 - Litres"])
        layout.addWidget(self.category_combo)

        # Purchase Rate
        layout.addWidget(QLabel("Purchase Rate"))
        self.purchase_rate_edit = QLineEdit()
        layout.addWidget(self.purchase_rate_edit)

        # Sale Rate
        layout.addWidget(QLabel("Sale Rate"))
        self.sale_rate_edit = QLineEdit()
        layout.addWidget(self.sale_rate_edit)

        # Quantity
        layout.addWidget(QLabel("Quantity"))
        self.quantity_edit = QLineEdit()
        layout.addWidget(self.quantity_edit)

        # Pre-fill if updating
        if part_data:
            self.name_edit.setText(str(part_data[1]))
            self.company_edit.setText(str(part_data[2]))
            self.category_combo.setCurrentIndex(0 if part_data[3] == 1 else 1)
            self.purchase_rate_edit.setText(str(part_data[4]))
            self.sale_rate_edit.setText(str(part_data[5]))
            self.quantity_edit.setText(str(part_data[7]))

        # Buttons
        btn_layout = QHBoxLayout()
        layout.addLayout(btn_layout)

        submit_btn = QPushButton("Submit")
        submit_btn.clicked.connect(self.accept)
        btn_layout.addWidget(submit_btn)

        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_btn)

    def get_data(self):
        return {
            "Name": self.name_edit.text(),
            "Company": self.company_edit.text(),
            "Category": self.category_combo.currentText(),
            "Purchase Rate": self.purchase_rate_edit.text(),
            "Sale Rate": self.sale_rate_edit.text(),
            "Quantity": self.quantity_edit.text(),
        }


class SellDialog(QDialog):
    def __init__(self, parent, part_data):
        super().__init__(parent)
        self.setWindowTitle("Sell Part")
        self.setFixedSize(400, 250)

        layout = QVBoxLayout(self)

        layout.addWidget(QLabel("Customer Name"))
        self.customer_edit = QLineEdit()
        layout.addWidget(self.customer_edit)

        layout.addWidget(QLabel("Quantity"))
        self.quantity_edit = QLineEdit()
        layout.addWidget(self.quantity_edit)

        btn_layout = QHBoxLayout()
        layout.addLayout(btn_layout)

        submit_btn = QPushButton("Sell")
        submit_btn.clicked.connect(self._validate_and_accept)
        btn_layout.addWidget(submit_btn)

        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_btn)

    def _validate_and_accept(self):
        if not self.customer_edit.text().strip():
            QMessageBox.warning(self, "Validation Error", "Please enter customer name.")
            return
        try:
            qty = float(self.quantity_edit.text())
            if qty <= 0:
                raise ValueError()
        except ValueError:
            QMessageBox.warning(self, "Validation Error", "Enter a valid quantity.")
            return
        self.accept()

    def get_data(self):
        return self.customer_edit.text().strip(), float(self.quantity_edit.text())
