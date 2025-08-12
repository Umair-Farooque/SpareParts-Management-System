import sqlite3
import datetime
import random
import json

class SaleManager:
    def __init__(self, db="inventory.db"):
        self.db = db
        self._init_table()

    def _init_table(self):
        with sqlite3.connect(self.db) as conn:
            # Drop old sales table if exists (optional, you may want to migrate instead)
            # conn.execute('DROP TABLE IF EXISTS sales')

            conn.execute('''
                CREATE TABLE IF NOT EXISTS sales (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT DEFAULT (datetime('now')),
                    items_json TEXT NOT NULL,
                    total_price REAL NOT NULL,
                    customer_name TEXT,
                    invoice_no TEXT UNIQUE
                )
            ''')
            conn.commit()

    def generate_invoice_no(self):
        now = datetime.datetime.now()
        return f"INV{now.strftime('%Y%m%d%H%M%S')}{random.randint(100,999)}"

    def record_sale(self, items, total_price, customer_name):
        """
        Record a sale containing multiple items.
        :param items: list of dicts, each dict has keys: barcode_id, name, quantity, price_per_unit, total_price
        :param total_price: float, total price of all items combined
        :param customer_name: string
        :return: invoice_no string
        """
        invoice_no = self.generate_invoice_no()
        items_json = json.dumps(items)

        with sqlite3.connect(self.db) as conn:
            conn.execute('''
                INSERT INTO sales (timestamp, items_json, total_price, customer_name, invoice_no)
                VALUES (datetime('now'), ?, ?, ?, ?)
            ''', (items_json, total_price, customer_name, invoice_no))
            conn.commit()
        return invoice_no

    def get_sales_summary(self):
        with sqlite3.connect(self.db) as conn:
            return conn.execute("SELECT COALESCE(SUM(total_price),0) FROM sales").fetchone()

    def get_all_sales(self):
        with sqlite3.connect(self.db) as conn:
            # Returns id, timestamp, items_json (string), total_price, customer_name, invoice_no
            return conn.execute("""
                SELECT id, timestamp, items_json, total_price, customer_name, invoice_no
                FROM sales
                ORDER BY timestamp DESC
            """).fetchall()

    def get_sale_by_invoice(self, invoice_no):
        with sqlite3.connect(self.db) as conn:
            return conn.execute("""
                SELECT id, timestamp, items_json, total_price, customer_name, invoice_no
                FROM sales
                WHERE invoice_no = ?
            """, (invoice_no,)).fetchone()
