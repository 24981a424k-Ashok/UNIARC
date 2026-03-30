import sqlite3
import os

db_path = 'data/news.db'
if os.path.exists(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("PRAGMA table_info(breaking_news)")
    columns = [col[1] for col in cursor.fetchall()]
    print(f"Columns in breaking_news: {', '.join(columns)}")
    conn.close()
else:
    print(f"{db_path} does not exist")
