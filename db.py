# c2/db.py
import sqlite3

DB_FILE = "c2_database.db"

def init_db():
    with sqlite3.connect(DB_FILE) as conn:
        c = conn.cursor()
        c.execute("""CREATE TABLE IF NOT EXISTS agents (
            agent_id TEXT PRIMARY KEY,
            ip TEXT, hostname TEXT, tags TEXT, last_seen TEXT)""")
        c.execute("""CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            agent_id TEXT, command TEXT, created_at TEXT)""")
        c.execute("""CREATE TABLE IF NOT EXISTS results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            agent_id TEXT, output TEXT, timestamp TEXT)""")
        conn.commit()

def get_conn():
    return sqlite3.connect(DB_FILE)
