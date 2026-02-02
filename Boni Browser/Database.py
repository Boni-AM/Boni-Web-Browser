from datetime import datetime, timedelta
import sqlite3
import bcrypt

class Database:
    def __init__(self, db_name="browser_users.db"):
        self.conn = sqlite3.connect(db_name)
        self.create_tables()

    def create_tables(self):
        c = self.conn.cursor()
        c.execute("""
            CREATE TABLE IF NOT EXISTS users (
                username TEXT PRIMARY KEY,
                password_hash BLOB NOT NULL
            )
        """)
        c.execute("""
            CREATE TABLE IF NOT EXISTS history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL,
                entry TEXT NOT NULL,
                entry_type TEXT NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        self.conn.commit()

    def add_user(self, username, password):
        if self.user_exists(username):
            return False
        pw_hash = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
        self.conn.execute("INSERT INTO users (username, password_hash) VALUES (?, ?)", (username, pw_hash))
        self.conn.commit()
        return True

    def user_exists(self, username):
        c = self.conn.cursor()
        c.execute("SELECT 1 FROM users WHERE username = ?", (username,))
        return c.fetchone() is not None

    def verify_user(self, username, password):
        c = self.conn.cursor()
        c.execute("SELECT password_hash FROM users WHERE username = ?", (username,))
        row = c.fetchone()
        if row is None:
            return False
        return bcrypt.checkpw(password.encode(), row[0])

    def save_history(self, username, entry, entry_type='search'):
        self.conn.execute(
            "INSERT INTO history (username, entry, entry_type) VALUES (?, ?, ?)",
            (username, entry, entry_type)
        )
        self.conn.commit()

    def get_user_history(self, username):
        c = self.conn.cursor()
        c.execute(
            "SELECT entry, entry_type, timestamp FROM history WHERE username = ? ORDER BY timestamp DESC",
            (username,)
        )
        rows = c.fetchall()

        converted = []
        for entry, etype, ts in rows:
            dt = datetime.strptime(ts, '%Y-%m-%d %H:%M:%S')
            dt_utc_plus_2 = dt + timedelta(hours=2)
            ts_str = dt_utc_plus_2.strftime('%Y-%m-%d %H:%M:%S')
            converted.append((entry, etype, ts_str))
        return converted

    def clear_user_history(self, username):
        self.conn.execute("DELETE FROM history WHERE username = ?", (username,))
        self.conn.commit()
