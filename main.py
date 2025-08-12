import sys
from PyQt6.QtWidgets import QApplication
from login_window import LoginWindow
from auth_manager import AuthManager
from inventory_manager import InventoryManager
from sales_manager import SaleManager
from bill_printer import BillPrinter

def main():
    app = QApplication(sys.argv)

    auth = AuthManager()
    inventory = InventoryManager()
    sales = SaleManager()
    printer = BillPrinter()

    login_window = LoginWindow(auth, inventory, sales, printer)
    login_window.show()

    sys.exit(app.exec())

if __name__ == "__main__":
    main()
