import sqlite3
from config import DB_NAME

# =========================
# GET CONNECTION
# =========================
def get_connection():
    """
    Create and return a SQLite connection
    """
    conn = sqlite3.connect(DB_NAME, check_same_thread=False)
    return conn


# =========================
# INITIALIZE DATABASE
# =========================
def init_db():
    """
    Create tables if not exist
    """
    conn = get_connection()
    cur = conn.cursor()

    # USERS TABLE
    cur.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)
    conn.execute("""
    CREATE TABLE IF NOT EXISTS alerts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT,
        coin TEXT,
        condition TEXT,        -- 'above' or 'below'
        target_price REAL,
        active INTEGER DEFAULT 1
    )
    """)
    # HOLDINGS TABLE
    cur.execute("""
    CREATE TABLE IF NOT EXISTS holdings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT NOT NULL,
        crypto TEXT NOT NULL,
        amount REAL NOT NULL,
        date TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    conn.commit()
    conn.close()


# =========================
# CLOSE CONNECTION (OPTIONAL)
# =========================
def close_connection(conn):
    if conn:
        conn.close()
