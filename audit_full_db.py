import sqlite3
import os

db_path = "c:/Users/CH ASHOK REDDY/OneDrive/Desktop/VibeCoding/ai-news-agent/data/news.db"

def audit_db():
    if not os.path.exists(db_path):
        print("DB not found.")
        return
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = [t[0] for t in cursor.fetchall()]
    print(f"Tables: {tables}")
    
    for table in tables:
        print(f"\nColumns in '{table}':")
        cursor.execute(f"PRAGMA table_info({table});")
        cols = cursor.fetchall()
        for col in cols:
            print(f" - {col[1]} ({col[2]})")
            
    conn.close()

if __name__ == "__main__":
    audit_db()
