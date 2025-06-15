import sqlite3
import datetime
import random
import uuid


class SaleManager:
    def __init__(self, db="autos.db"):
        self.db = db
        self._init_table()

    def _init_table(self):
        with sqlite3.connect(self.db) as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS sales (
                    id INTEGER PRIMARY KEY,
                    part_id INTEGER,
                    quantity INTEGER,
                    total_price REAL,
                    timestamp TEXT,
                    customer_name TEXT,
                    invoice_no TEXT
                )
            ''')

            # Add missing column if not exists
            columns = [row[1] for row in conn.execute("PRAGMA table_info(sales)")]
            if "invoice_no" not in columns:
                conn.execute("ALTER TABLE sales ADD COLUMN invoice_no TEXT")


    def generate_Invoice_no(self):
        now = datetime.datetime.now()
        return f"INV{now.strftime('%Y%m%d%H%M%S')}{random.randint(100,999)}"

    import uuid  # at top of file

    def record_sale(self, part_id, quantity, total, customer_name):
        invoice_no = str(uuid.uuid4())[:8]  # generate short unique invoice number
        with sqlite3.connect(self.db) as conn:
            conn.execute('''
                INSERT INTO sales (part_id, quantity, total_price, timestamp, customer_name, invoice_no)
                VALUES (?, ?, ?, datetime('now'), ?, ?)
            ''', (part_id, quantity, total, customer_name, invoice_no))
        return invoice_no

    def get_sales_summary(self):
        with sqlite3.connect(self.db) as conn:
            return conn.execute("SELECT SUM(quantity), SUM(total_price) FROM sales").fetchone()

    def get_all_sales(self):
        with sqlite3.connect(self.db) as conn:
            return conn.execute("""
                SELECT s.id, s.timestamp, p.name, s.quantity, s.total_price, s.customer_name, s.invoice_no
                FROM sales s
                JOIN parts p ON s.part_id = p.id
                ORDER BY s.timestamp DESC
            """).fetchall()

    def get_sale_by_invoice(self, invoice_no):
        with sqlite3.connect(self.db) as conn:
            return conn.execute("""
                SELECT s.id, s.timestamp, p.name, s.quantity, s.total_price, s.customer_name, s.invoice_no
                FROM sales s
                JOIN parts p ON s.part_id = p.id
                WHERE s.invoice_no = ?
            """, (invoice_no,)).fetchone()
