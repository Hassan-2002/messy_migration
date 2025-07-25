import sqlite3
import os
from werkzeug.security import generate_password_hash

DATABASE_PATH = 'instance/users.db'

def init_db():
    os.makedirs(os.path.dirname(DATABASE_PATH), exist_ok=True)

    conn = None
    try:
        conn = sqlite3.connect(DATABASE_PATH)
        cursor = conn.cursor()

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                password_hash TEXT NOT NULL,
                email TEXT UNIQUE
            )
        ''')

        admin_password_hash = generate_password_hash('adminpass')

        cursor.execute("INSERT OR IGNORE INTO users (name, password_hash, email) VALUES (?, ?, ?)",
                       ('admin', admin_password_hash, 'admin@example.com'))

        conn.commit()
        print(f"Database initialized and default user 'admin' added to '{DATABASE_PATH}'.")

    except sqlite3.Error as e:
        print(f"Database initialization error: {e}")
    finally:
        if conn:
            conn.close()

if __name__ == '__main__':
    init_db()
