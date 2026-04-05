import sqlite3
import os
from src.config.settings import DATABASE_URL

def fix_db():
    print(f"Connecting to database at: {DATABASE_URL}")
    if not DATABASE_URL.startswith("sqlite"):
        print("Not a SQLite database, skipping manual migration.")
        return

    db_path = DATABASE_URL.replace("sqlite:///", "")
    if not os.path.exists(db_path):
        print(f"Database file not found at {db_path}")
        return

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if column exists
        cursor.execute("PRAGMA table_info(users)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if "profile_image_url" not in columns:
            print("Adding 'profile_image_url' column to 'users' table...")
            cursor.execute("ALTER TABLE users ADD COLUMN profile_image_url TEXT")
            conn.commit()
            print("Column added successfully.")
        else:
            print("Column 'profile_image_url' already exists.")
            
        conn.close()
    except Exception as e:
        print(f"Error fixing database: {e}")

if __name__ == "__main__":
    fix_db()
