import sqlite3
import os
import json

DB_PATH = os.path.join("data", "news.db")

def check_db():
    if not os.path.exists(DB_PATH):
        print(f"[FAIL] Database not found at {DB_PATH}")
        return

    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        print("--- DATABASE STATUS ---")
        
        # Check DailyDigest
        try:
            cursor.execute("SELECT count(*) FROM daily_digests")
            count = cursor.fetchone()[0]
            print(f"Daily Digests: {count}")
            
            cursor.execute("SELECT date, is_published, content_json FROM daily_digests ORDER BY date DESC LIMIT 1")
            row = cursor.fetchone()
            if row:
                print(f"Latest Digest: {row[0]} (Published: {row[1]})")
                content = json.loads(row[2])
                print(f"  - Top Stories: {len(content.get('top_stories', []))}")
                print(f"  - Breaking News: {len(content.get('breaking_news', []))}")
                print(f"  - Premium Intel: {len(content.get('premium_intel', []))}")
            else:
                print("Latest Digest: NONE")
        except Exception as e:
            print(f"Error reading daily_digests: {e}")

        # Check raw_news
        try:
            cursor.execute("SELECT count(*) FROM raw_news")
            raw_count = cursor.fetchone()[0]
            print(f"Raw News Count: {raw_count}")
        except Exception as e:
            print(f"Error reading raw_news: {e}")
            
        conn.close()
        print("-----------------------")
    except Exception as e:
        print(f"[DB] Error checking database: {e}")

if __name__ == "__main__":
    check_db()
