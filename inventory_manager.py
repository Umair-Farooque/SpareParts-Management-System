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

            # Your actual categories table schema
            cur.execute("""
                CREATE TABLE IF NOT EXISTS categories (
                    category_id INTEGER PRIMARY KEY,
                    category_name TEXT NOT NULL UNIQUE
                )
            """)

            cur.execute("""
                CREATE TABLE IF NOT EXISTS products (
                    barcode_id TEXT PRIMARY KEY,
                    item_name TEXT NOT NULL,
                    company TEXT,
                    purchase_rate REAL,
                    sale_rate REAL,
                    category_id INTGER,
                    FOREIGN KEY (category_id) REFERENCES categories(category_id)
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

    # Add category by integer and name, only needed initially
    def add_category(self, category_id, category_name):
        with sqlite3.connect(self.db) as conn:
            conn.execute(
                "INSERT OR IGNORE INTO categories (category_id, category_name) VALUES (?, ?)",
                (category_id, category_name)
            )
            conn.commit()

    # Get category_name by category_id int
    def get_category_name(self, category_id):
        with sqlite3.connect(self.db) as conn:
            row = conn.execute(
                "SELECT category_name FROM categories WHERE category_id=?",
                (category_id,)
            ).fetchone()
            return row[0] if row else None

    # Generate barcode image with text below
    def _generate_barcode(self, barcode_id):
        filename = os.path.join(self.barcode_dir, f"{barcode_id}.png")

        code128 = barcode.get('code128', str(barcode_id), writer=ImageWriter())
        code128.save(filename.replace(".png", ""))

        img = Image.open(filename)
        draw = ImageDraw.Draw(img)

        try:
            font = ImageFont.truetype("arial.ttf", 16)
        except:
            font = ImageFont.load_default()

        # Get text bounding box using textbbox
        bbox = draw.textbbox((0, 0), str(barcode_id), font=font)
        text_w = bbox[2] - bbox[0]  # right - left
        text_h = bbox[3] - bbox[1]  # bottom - top
        
        img_w, img_h = img.size

        new_img = Image.new("RGB", (img_w, img_h + text_h + 10), "white")
        new_img.paste(img, (0, 0))
        draw = ImageDraw.Draw(new_img)
        draw.text(((img_w - text_w) // 2, img_h + 5), str(barcode_id), fill="black", font=font)

        new_img.save(filename)

    # Add or update a product
    # category here is integer (1 or 2)
    def add_product(self, barcode_id=None, name=None, company=None, category_id=None, purchase_rate=None, sale_rate=None, amount=None):
        if barcode_id is None:
            import time, random
            barcode_id = f"{int(time.time())}{random.randint(100,999)}"

        # Ensure category exists, if not create it
        category_id = int(category_id)  # Ensure category is an integer
        if category_id not in [1, 2]:
            category_id = 1  # Default to Quantity if invalid
            
        # Add the category if it doesn't exist
        with sqlite3.connect(self.db) as conn:
            # Check if category exists
            cur = conn.cursor()
            cur.execute("SELECT category_name FROM categories WHERE category_id = ?", (category_id,))
            if not cur.fetchone():
                # Add the category
                category_name = "Quantity" if category_id == 1 else "Litres"
                conn.execute(
                    "INSERT INTO categories (category_id, category_name) VALUES (?, ?)",
                    (category_id, category_name)
                )
                conn.commit()

        # Set unit_type based on category (1=Quantity, 2=Litres)
        unit_type = "Quantity" if category_id == 1 else "Litres"

        with sqlite3.connect(self.db) as conn:
            conn.execute("""
                INSERT OR REPLACE INTO products
                (barcode_id, item_name, company, category_id, purchase_rate, sale_rate)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (barcode_id, name, company, category_id, purchase_rate, sale_rate))

            conn.execute("""
                INSERT OR REPLACE INTO stock_units
                (barcode_id, unit_type, amount)
                VALUES (?, ?, ?)
            """, (barcode_id, unit_type, amount))

            conn.commit()

        self._generate_barcode(barcode_id)
        return barcode_id

    def delete_product(self, barcode_id):
        with sqlite3.connect(self.db) as conn:
            conn.execute("DELETE FROM stock_units WHERE barcode_id=?", (barcode_id,))
            conn.execute("DELETE FROM products WHERE barcode_id=?", (barcode_id,))
            conn.commit()

        barcode_file = os.path.join(self.barcode_dir, f"{barcode_id}.png")
        if os.path.exists(barcode_file):
            os.remove(barcode_file)

    def get_product(self, barcode_id):
        with sqlite3.connect(self.db) as conn:
            return conn.execute("""
                SELECT p.barcode_id, p.item_name, p.company, c.category_name as category_id,
                       p.purchase_rate, p.sale_rate, s.unit_type, s.amount
                FROM products p
                LEFT JOIN categories c ON p.category_id = c.category_id
                LEFT JOIN stock_units s ON p.barcode_id = s.barcode_id
                WHERE p.barcode_id = ?
            """, (barcode_id,)).fetchone()

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
