import sqlite3

class AuthManager:
    def __init__(self, db="inventory.db"):
        self.db = db
        self._init_table()

    def _init_table(self):
        with sqlite3.connect(self.db) as conn:
            conn.execute('''CREATE TABLE IF NOT EXISTS users (
                username TEXT PRIMARY KEY,
                password TEXT,
                question TEXT,
                answer TEXT
            )''')
            conn.execute("INSERT OR IGNORE INTO users VALUES (?, ?, ?, ?)",
                         ("admin", "admin123", "Favorite color?", "blue"))

    def validate_login(self, u, p):
        with sqlite3.connect(self.db) as conn:
            res = conn.execute("SELECT * FROM users WHERE username=? AND password=?", (u, p)).fetchone()
            return bool(res)

    def reset_password(self, u, q, a, new_p):
        with sqlite3.connect(self.db) as conn:
            row = conn.execute("SELECT * FROM users WHERE username=? AND question=? AND answer=?", (u, q, a)).fetchone()
            if row:
                conn.execute("UPDATE users SET password=? WHERE username=?", (new_p, u))
                return True
            return False

    def change_password(self, u, old_p, new_p):
        if not self.validate_login(u, old_p): return False
        with sqlite3.connect(self.db) as conn:
            conn.execute("UPDATE users SET password=? WHERE username=?", (new_p, u))
        return True
    
    def register_user(self, username, password, question, answer):
        try:
            with sqlite3.connect(self.db) as conn:
                conn.execute("INSERT INTO users VALUES (?, ?, ?, ?)", (username, password, question, answer))
            return True
        except sqlite3.IntegrityError:
            return False  # Username already exists

