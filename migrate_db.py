
import sqlite3
import os

db_path = "data/news.db"

def migrate():
    if not os.path.exists(db_path):
        print(f"Database not found at {db_path}")
        return

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    print("Checking for missing columns...")

    # verified_news
    cursor.execute("PRAGMA table_info(verified_news)")
    columns = [col[1] for col in cursor.fetchall()]
    
    if "is_fake" not in columns:
        print("Adding 'is_fake' to verified_news...")
        cursor.execute("ALTER TABLE verified_news ADD COLUMN is_fake BOOLEAN DEFAULT 0")
    
    if "flag_count" not in columns:
        print("Adding 'flag_count' to verified_news...")
        cursor.execute("ALTER TABLE verified_news ADD COLUMN flag_count INTEGER DEFAULT 0")

    # users
    cursor.execute("PRAGMA table_info(users)")
    columns = [col[1] for col in cursor.fetchall()]

    if "bounty_points" not in columns:
        print("Adding 'bounty_points' to users...")
        cursor.execute("ALTER TABLE users ADD COLUMN bounty_points INTEGER DEFAULT 0")

    conn.commit()
    conn.close()
    print("Migration completed successfully.")

if __name__ == "__main__":
    migrate()
