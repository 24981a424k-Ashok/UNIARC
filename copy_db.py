import shutil
import os

src = "c:/Users/CH ASHOK REDDY/OneDrive/Desktop/VibeCoding/ai-news-agent/src/data/news.db"
dest = "c:/Users/CH ASHOK REDDY/OneDrive/Desktop/VibeCoding/ai-news-agent/data/news.db"

if os.path.exists(src):
    print(f"Copying {src} to {dest}...")
    shutil.copy2(src, dest)
    print("Copy complete.")
else:
    print(f"Source file {src} not found!")

# Verify after copy
import sqlite3
def check_db(path):
    print(f"Verifying {path}...")
    try:
        conn = sqlite3.connect(path)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = [t[0] for t in cursor.fetchall()]
        print(f"Tables: {tables}")
        conn.close()
    except Exception as e:
        print(f"Error: {e}")

check_db(dest)
