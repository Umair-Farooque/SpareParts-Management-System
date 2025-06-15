import sqlite3

class InventoryManager:
    def __init__(self, db="autos.db"):
        self.db = db
        self._init_table()

    def _init_table(self):
        with sqlite3.connect(self.db) as conn:
            conn.execute('''CREATE TABLE IF NOT EXISTS parts (
                id INTEGER PRIMARY KEY,
                name TEXT,
                part_no TEXT,
                price REAL,
                qty INTEGER
            )''')

    def add_part(self, name, part_no, price, qty):
        with sqlite3.connect(self.db) as conn:
            conn.execute("INSERT INTO parts (name, part_no, price, qty) VALUES (?, ?, ?, ?)",
                         (name, part_no, price, qty))

    def delete_part(self, part_id):
        with sqlite3.connect(self.db) as conn:
            conn.execute("DELETE FROM parts WHERE id=?", (part_id,))

    def get_all_parts(self):
        with sqlite3.connect(self.db) as conn:
            return conn.execute("SELECT * FROM parts").fetchall()

    def update_qty(self, part_id, qty_diff):
        with sqlite3.connect(self.db) as conn:
            conn.execute("UPDATE parts SET qty = qty + ? WHERE id = ?", (qty_diff, part_id))

