from PyQt6.QtWidgets import (
    QDialog, QLabel, QLineEdit, QPushButton, QVBoxLayout, QMessageBox
)
from PyQt6.QtCore import Qt


class InvoiceSearchWindow(QDialog):
    def __init__(self, sales_manager, printer=None, parent=None):
        super().__init__(parent)
        self.sales_manager = sales_manager
        self.printer = printer

        self.setWindowTitle("Search Invoice")
        self.setFixedSize(400, 180)
        self._center_window()

        layout = QVBoxLayout()
        self.setLayout(layout)

        layout.addWidget(QLabel("Enter Invoice Number"))

        self.entry = QLineEdit()
        layout.addWidget(self.entry)

        search_btn = QPushButton("Search")
        search_btn.clicked.connect(self.search)
        layout.addWidget(search_btn)

    def _center_window(self):
        self.setGeometry(
            (self.screen().geometry().width() - self.width()) // 2,
            (self.screen().geometry().height() - self.height()) // 2,
            self.width(),
            self.height()
        )

    def search(self):
        invoice_no = self.entry.text().strip()
        print(f"Searching for invoice: {invoice_no}")  # Debug print

        if not invoice_no:
            QMessageBox.warning(self, "Input Error", "Please enter an invoice number.")
            return

        result = self.sales_manager.get_sale_by_invoice(invoice_no)
        print(f"Result from sales_manager: {result}")  # Debug print

        if not result:
            QMessageBox.critical(self, "Not Found", "No sale found with this invoice number.")
            return

        sale_id, timestamp, part_name, qty, total, customer_name, invoice = result

        if not self.printer:
            QMessageBox.critical(self, "Printer Error", "No printer configured.")
            return

        bill_text = self.printer.generate_bill(customer_name, [{
            "name": part_name,
            "qty": qty,
            "total": total
        }], invoice_no=invoice)

        print("Printing bill...")  # Debug print
        self.printer.print_bill(bill_text)

        QMessageBox.information(self, "Success", "Invoice printed successfully.")
        self.close()
