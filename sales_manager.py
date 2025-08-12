# sale_manager.py
import sqlite3
import datetime
import random
import uuid

class SaleManager:
    def __init__(self, db="inventory.db"):
        self.db = db
        self._init_table()

    def _init_table(self):
        with sqlite3.connect(self.db) as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS sales (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    barcode_id TEXT,
                    quantity INTEGER,
                    total_price REAL,
                    timestamp TEXT DEFAULT (datetime('now')),
                    customer_name TEXT,
                    invoice_no TEXT
                )
            ''')
            # ensure invoice_no exists (it is created above so this is just defensive)
            conn.commit()

    def generate_invoice_no(self):
        now = datetime.datetime.now()
        return f"INV{now.strftime('%Y%m%d%H%M%S')}{random.randint(100,999)}"

    def record_sale(self, barcode_id, quantity, total, customer_name):
        # barcode_id is TEXT (e.g., INV0001)
        invoice_no = str(uuid.uuid4())[:8]
        with sqlite3.connect(self.db) as conn:
            conn.execute('''
                INSERT INTO sales (barcode_id, quantity, total_price, timestamp, customer_name, invoice_no)
                VALUES (?, ?, ?, datetime('now'), ?, ?)
            ''', (barcode_id, quantity, total, customer_name, invoice_no))
        return invoice_no

    def get_sales_summary(self):
        with sqlite3.connect(self.db) as conn:
            return conn.execute("SELECT COALESCE(SUM(quantity),0), COALESCE(SUM(total_price),0) FROM sales").fetchone()

    def get_all_sales(self):
        with sqlite3.connect(self.db) as conn:
            return conn.execute("""
                SELECT s.id, s.timestamp, p.item_name, s.quantity, s.total_price, s.customer_name, s.invoice_no
                FROM sales s
                LEFT JOIN products p ON s.barcode_id = p.barcode_id
                ORDER BY s.timestamp DESC
            """).fetchall()

    def get_sale_by_invoice(self, invoice_no):
        with sqlite3.connect(self.db) as conn:
            return conn.execute("""
                SELECT s.id, s.timestamp, p.name, s.quantity, s.total_price, s.customer_name, s.invoice_no
                FROM sales s
                LEFT JOIN products p ON s.barcode_id = p.barcode_id
                WHERE s.invoice_no = ?
            """, (invoice_no,)).fetchone()
