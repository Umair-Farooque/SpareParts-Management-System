from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QTableWidget, QTableWidgetItem, QPushButton, QMessageBox
)
from PyQt6.QtCore import Qt
import json

class SaleWindow(QDialog):
    def __init__(self, sales_manager, printer=None, parent=None):
        super().__init__(parent)
        self.sales_manager = sales_manager
        self.printer = printer

        self.setWindowTitle("Sales History")
        self.resize(800, 400)
        self._setup_ui()
        self.populate_table()

    def _setup_ui(self):
        layout = QVBoxLayout(self)

        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(["ID", "Time", "Items", "Total", "Customer", "Invoice"])
        self.table.horizontalHeader().setStretchLastSection(True)
        self.table.setSelectionBehavior(self.table.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(self.table.SelectionMode.SingleSelection)
        layout.addWidget(self.table)

        if self.printer:
            self.print_btn = QPushButton("Print Selected Bill")
            self.print_btn.clicked.connect(self.print_selected)
            layout.addWidget(self.print_btn)

    def populate_table(self):
        sales = self.sales_manager.get_all_sales()
        self.table.setRowCount(0)

        for row in sales:
            sale_id, timestamp, items_json, total, customer_name, invoice_no = row
            try:
                items = json.loads(items_json)
                items_str = ", ".join(f"{item['name']} x{item['quantity']}" for item in items)
            except Exception:
                items_str = "Error parsing items"

            row_pos = self.table.rowCount()
            self.table.insertRow(row_pos)
            self.table.setItem(row_pos, 0, QTableWidgetItem(str(sale_id)))
            self.table.setItem(row_pos, 1, QTableWidgetItem(str(timestamp)))
            self.table.setItem(row_pos, 2, QTableWidgetItem(items_str))
            self.table.setItem(row_pos, 3, QTableWidgetItem(str(total)))
            self.table.setItem(row_pos, 4, QTableWidgetItem(customer_name))
            self.table.setItem(row_pos, 5, QTableWidgetItem(str(invoice_no)))

    def print_selected(self):
        selected_rows = self.table.selectionModel().selectedRows()
        if not selected_rows:
            QMessageBox.warning(self, "No Selection", "Please select a sale to print.")
            return

        row = selected_rows[0].row()
        invoice_no = self.table.item(row, 5).text()
        customer_name = self.table.item(row, 4).text()

        sale_record = self.sales_manager.get_sale_by_invoice(invoice_no)
        if not sale_record:
            QMessageBox.critical(self, "Error", "Could not retrieve sale details.")
            return

        _, _, items_json, _, _, _ = sale_record
        try:
            items = json.loads(items_json)
        except Exception:
            QMessageBox.critical(self, "Error", "Failed to parse sale items.")
            return

        bill_text = self.printer.generate_bill(customer_name, items, invoice_no=invoice_no)
        self.printer.print_bill(bill_text)
