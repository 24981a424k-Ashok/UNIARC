import sqlite3
import os
from pathlib import Path

# Target the specific database file
DB_PATH = "data/news.db"

def migrate():
    if not os.path.exists(DB_PATH):
        print(f"Error: {DB_PATH} not found.")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Get current columns
    cursor.execute("PRAGMA table_info(users)")
    columns = [c[1] for c in cursor.fetchall()]
    print(f"Current columns in 'users' table: {columns}")

    needed_columns = {
        "profile_image_url": "TEXT",
        "streak_history": "JSON",
        "subscription_status": "TEXT DEFAULT 'free'",
        "bio": "TEXT",
        "current_streak": "INTEGER DEFAULT 0"
    }

    for col, col_type in needed_columns.items():
        if col not in columns:
            print(f"Adding column: {col}")
            try:
                cursor.execute(f"ALTER TABLE users ADD COLUMN {col} {col_type}")
            except Exception as e:
                print(f"Failed to add {col}: {e}")
        else:
            print(f"Column {col} already exists.")

    conn.commit()
    conn.close()
    print("Migration complete.")

if __name__ == "__main__":
    migrate()
