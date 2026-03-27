import sqlite3
import os

def check_breaking(db_path, output_file):
    with open(output_file, 'a') as f:
        f.write(f"\nChecking database: {db_path}\n")
        if not os.path.exists(db_path):
            f.write("File not found.\n")
            return
        
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Check if table exists
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='breaking_news';")
            if not cursor.fetchone():
                f.write("Table 'breaking_news' does not exist.\n")
                return
                
            cursor.execute("SELECT COUNT(*) FROM breaking_news;")
            count = cursor.fetchone()[0]
            f.write(f"Total Breaking News items: {count}\n")
            
            if count > 0:
                cursor.execute("SELECT breaking_headline, created_at FROM breaking_news LIMIT 5;")
                for row in cursor.fetchall():
                    f.write(f" - {row[0]} ({row[1]})\n")
                    
            # Also check DailyDigest
            cursor.execute("SELECT COUNT(*) FROM daily_digests;")
            digest_count = cursor.fetchone()[0]
            f.write(f"Total Daily Digests: {digest_count}\n")
            
            if digest_count > 0:
                cursor.execute("SELECT date FROM daily_digests ORDER BY date DESC LIMIT 1;")
                f.write(f"Latest digest date: {cursor.fetchone()[0]}\n")
                
            conn.close()
        except Exception as e:
            f.write(f"Error: {e}\n")

if __name__ == "__main__":
    out = "check_results.txt"
    if os.path.exists(out): os.remove(out)
    check_breaking("c:/Users/CH ASHOK REDDY/OneDrive/Desktop/VibeCoding/ai-news-agent/data/news.db", out)
    check_breaking("c:/Users/CH ASHOK REDDY/OneDrive/Desktop/VibeCoding/ai-news-agent/src/data/news.db", out)
    check_breaking("c:/Users/CH ASHOK REDDY/OneDrive/Desktop/VibeCoding/ai-news-agent/news.db", out)
    check_breaking("./news.db", out)
    print("Done. Results in check_results.txt")
