import sqlite3
import os

db_path = "c:/Users/CH ASHOK REDDY/OneDrive/Desktop/VibeCoding/ai-news-agent/data/news.db"

def check_counts():
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    tables = ['raw_news', 'verified_news', 'breaking_news', 'daily_digests']
    
    for table in tables:
        cursor.execute(f"SELECT COUNT(*) FROM {table}")
        count = cursor.fetchone()[0]
        print(f"{table}: {count}")
    
    conn.close()

if __name__ == "__main__":
    check_counts()
