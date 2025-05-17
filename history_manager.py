import sqlite3
from datetime import datetime


class HistoryManager:
    def __init__(self):
        self.db_path = "data/history.db"
        self._init_db()

    def _init_db(self):
        """Initialize the history database"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS history (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        url TEXT NOT NULL,
                        title TEXT,
                        timestamp TEXT NOT NULL
                    )
                """)
                conn.commit()
        except sqlite3.Error as e:
            print(f"Error initializing history database: {e}")

    def add_entry(self, url, title):
        """Add a new history entry"""
        if not url:
            return

        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                timestamp = datetime.now().isoformat()
                cursor.execute(
                    "INSERT INTO history (url, title, timestamp) VALUES (?, ?, ?)",
                    (url, title, timestamp)
                )
                conn.commit()
        except sqlite3.Error as e:
            print(f"Error adding history entry: {e}")

    def get_history(self, limit=100):
        """Retrieve history entries"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT url, title, timestamp FROM history ORDER BY timestamp DESC LIMIT ?",
                    (limit,)
                )
                return cursor.fetchall()
        except sqlite3.Error as e:
            print(f"Error retrieving history: {e}")
            return []

    def search_history(self, query, limit=50):
        """Search history for entries matching the query"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT url, title, timestamp FROM history WHERE url LIKE ? OR title LIKE ? ORDER BY timestamp DESC LIMIT ?",
                    (f"%{query}%", f"%{query}%", limit)
                )
                return cursor.fetchall()
        except sqlite3.Error as e:
            print(f"Error searching history: {e}")
            return []

    def clear_history(self):
        """Clear all history entries"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM history")
                conn.commit()
        except sqlite3.Error as e:
            print(f"Error clearing history: {e}")

    def delete_entry(self, url):
        """Delete a specific history entry"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM history WHERE url = ?", (url,))
                conn.commit()
        except sqlite3.Error as e:
            print(f"Error deleting history entry: {e}")
