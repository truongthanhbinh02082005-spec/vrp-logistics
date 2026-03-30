import sqlite3
import os

db_path = 'backend/db.sqlite3'
if not os.path.exists(db_path):
    print(f"DB not found at {db_path}")
else:
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = [row[0] for row in cur.fetchall()]
    print("Tables found:")
    for t in sorted(tables):
        print(f"  {t}")
    conn.close()
