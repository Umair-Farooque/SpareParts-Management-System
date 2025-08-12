import sqlite3
import os
from PIL import Image, ImageDraw, ImageFont
import barcode
from barcode.writer import ImageWriter

class InventoryManager:
    def __init__(self, db="inventory.db", barcode_dir="barcodes"):
        self.db = db
        self.barcode_dir = barcode_dir
        os.makedirs(self.barcode_dir, exist_ok=True)
        self._init_tables()

    def _init_tables(self):
        with sqlite3.connect(self.db) as conn:
            cur = conn.cursor()

            cur.execute("""
                CREATE TABLE IF NOT EXISTS categories (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL UNIQUE
                )
            """)

            cur.execute("""
                CREATE TABLE IF NOT EXISTS products (
                    barcode_id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    company TEXT,
                    category_id INTEGER,
                    purchase_rate REAL,
                    sale_rate REAL,
                    FOREIGN KEY (category_id) REFERENCES categories(id)
                )
            """)

            cur.execute("""
                CREATE TABLE IF NOT EXISTS stock_units (
                    barcode_id TEXT PRIMARY KEY,
                    unit_type TEXT NOT NULL,
                    amount REAL NOT NULL,
                    FOREIGN KEY (barcode_id) REFERENCES products(barcode_id)
                )
            """)

            conn.commit()

    # --- Category Methods ---
    def add_category(self, name):
        with sqlite3.connect(self.db) as conn:
            conn.execute("INSERT OR IGNORE INTO categories (name) VALUES (?)", (name,))
            conn.commit()

    def get_category_id(self, name):
        with sqlite3.connect(self.db) as conn:
            row = conn.execute("SELECT id FROM categories WHERE name=?", (name,)).fetchone()
            return row[0] if row else None

    # --- Barcode Generation ---
    def _generate_barcode(self, barcode_id):
        filename = os.path.join(self.barcode_dir, f"{barcode_id}.png")

        # Generate barcode image
        code128 = barcode.get('code128', str(barcode_id), writer=ImageWriter())
        code128.save(filename.replace(".png", ""))

        # Open and add text
        img = Image.open(filename)
        draw = ImageDraw.Draw(img)

        try:
            font = ImageFont.truetype("arial.ttf", 16)
        except:
            font = ImageFont.load_default()

        text_w, text_h = draw.textsize(str(barcode_id), font=font)
        img_w, img_h = img.size

        # Create new image with space for text
        new_img = Image.new("RGB", (img_w, img_h + text_h + 10), "white")
        new_img.paste(img, (0, 0))
        draw = ImageDraw.Draw(new_img)
        draw.text(((img_w - text_w) / 2, img_h + 5), str(barcode_id), fill="black", font=font)

        new_img.save(filename)

    # --- Product Methods ---
    def add_product(self, barcode_id, name, company, category_name, purchase_rate, sale_rate, unit_type, amount):
        with sqlite3.connect(self.db) as conn:
            self.add_category(category_name)
            category_id = self.get_category_id(category_name)

            conn.execute("""
                INSERT OR REPLACE INTO products (barcode_id, name, company, category_id, purchase_rate, sale_rate)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (barcode_id, name, company, category_id, purchase_rate, sale_rate))

            conn.execute("""
                INSERT OR REPLACE INTO stock_units (barcode_id, unit_type, amount)
                VALUES (?, ?, ?)
            """, (barcode_id, unit_type, amount))

            conn.commit()

        # Generate barcode after product is successfully added
        self._generate_barcode(barcode_id)

    def delete_product(self, barcode_id):
        with sqlite3.connect(self.db) as conn:
            conn.execute("DELETE FROM stock_units WHERE barcode_id=?", (barcode_id,))
            conn.execute("DELETE FROM products WHERE barcode_id=?", (barcode_id,))
            conn.commit()

        # Remove barcode image
        barcode_file = os.path.join(self.barcode_dir, f"{barcode_id}.png")
        if os.path.exists(barcode_file):
            os.remove(barcode_file)

    def get_product(self, barcode_id):
        with sqlite3.connect(self.db) as conn:
            return conn.execute("""
                SELECT p.barcode_id, p.name, p.company, c.name as category,
                       p.purchase_rate, p.sale_rate, s.unit_type, s.amount
                FROM products p
                LEFT JOIN categories c ON p.category_id = c.id
                LEFT JOIN stock_units s ON p.barcode_id = s.barcode_id
                WHERE p.barcode_id = ?
            """, (barcode_id,)).fetchone()
            
        # --- Compatibility alias for old code ---
    def get_all_parts(self):
        return self.get_all_products()

    def get_all_products(self):
        with sqlite3.connect(self.db) as conn:
            return conn.execute("""
            SELECT 
                p.barcode_id,
                p.item_name,
                p.company,
                p.purchase_rate,
                p.sale_rate,
                s.amount
            FROM products p
            LEFT JOIN stock_units s ON p.barcode_id = s.barcode_id
        """).fetchall()


    def update_stock(self, barcode_id, amount_change):
        with sqlite3.connect(self.db) as conn:
            conn.execute("""
                UPDATE stock_units
                SET amount = amount + ?
                WHERE barcode_id = ?
            """, (amount_change, barcode_id))
            conn.commit()