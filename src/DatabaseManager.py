import sqlite3
from queue import Queue
from threading import Lock


class DatabaseManager:
    def __init__(self):
        self.db_path = 'clipboard_monitor.db'
        self.connection_pool = Queue()
        self.pool_lock = Lock()
        self.create_tables()

    def get_connection(self):
        with self.pool_lock:
            if self.connection_pool.empty():
                return sqlite3.connect(self.db_path, check_same_thread=False)
            return self.connection_pool.get()

    def return_connection(self, conn):
        self.connection_pool.put(conn)

    def create_tables(self):
        conn = self.get_connection()
        try:
            with conn:
                conn.execute('''
                    CREATE TABLE IF NOT EXISTS settings (
                        key TEXT PRIMARY KEY,
                        value TEXT
                    )
                ''')
                conn.execute('''
                    CREATE TABLE IF NOT EXISTS copy_history (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                        files_count INTEGER,
                        lines_count INTEGER,
                        content TEXT,
                        summary TEXT
                    )
                ''')
        finally:
            self.return_connection(conn)

    def get_setting(self, key, default=None):
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute('SELECT value FROM settings WHERE key = ?', (key,))
            result = cursor.fetchone()
            return result[0] if result else default
        finally:
            self.return_connection(conn)

    def set_setting(self, key, value):
        conn = self.get_connection()
        try:
            with conn:
                conn.execute('INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)', (key, str(value)))
        finally:
            self.return_connection(conn)

    def add_copy_history(self, files_count, lines_count, content):
        conn = self.get_connection()
        try:
            with conn:
                cursor = conn.cursor()
                cursor.execute('INSERT INTO copy_history (files_count, lines_count, content) VALUES (?, ?, ?)',
                               (files_count, lines_count, content))
                # Limit history to 20 items
                cursor.execute('''DELETE FROM copy_history WHERE id NOT IN
                                  (SELECT id FROM copy_history ORDER BY timestamp DESC LIMIT 20)''')
                return cursor.lastrowid
        finally:
            self.return_connection(conn)

    def update_copy_history_summary(self, item_id, summary):
        conn = self.get_connection()
        try:
            with conn:
                conn.execute('UPDATE copy_history SET summary = ? WHERE id = ?', (summary, item_id))
        finally:
            self.return_connection(conn)

    def get_copy_history(self):
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute(
                'SELECT id, files_count, lines_count, content, summary FROM copy_history ORDER BY timestamp DESC LIMIT 20')
            return cursor.fetchall()
        finally:
            self.return_connection(conn)

    def get_history_item_content(self, item_id):
        conn = self.get_connection()
        try:
            cursor = conn.cursor()
            cursor.execute('SELECT content FROM copy_history WHERE id = ?', (item_id,))
            result = cursor.fetchone()
            return result[0] if result else None
        finally:
            self.return_connection(conn)

    def close(self):
        while not self.connection_pool.empty():
            conn = self.connection_pool.get()
            conn.close()
