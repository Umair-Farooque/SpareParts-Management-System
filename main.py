from login_window import LoginWindow
from auth_manager import AuthManager
from inventory_manager import InventoryManager
from sales_manager import SaleManager
from bill_printer import BillPrinter

def main():
    auth = AuthManager()
    inventory = InventoryManager()
    sales = SaleManager()
    printer = BillPrinter()
    LoginWindow(auth, inventory, sales, printer)

if __name__ == "__main__":
    main()
