import sqlite3

def check_db(path):
    print(f"Checking {path}...")
    try:
        conn = sqlite3.connect(path)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = [t[0] for t in cursor.fetchall()]
        print(f"Tables: {tables}")
        conn.close()
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    check_db("c:/Users/CH ASHOK REDDY/OneDrive/Desktop/VibeCoding/ai-news-agent/data/news.db")
    check_db("c:/Users/CH ASHOK REDDY/OneDrive/Desktop/VibeCoding/ai-news-agent/src/data/news.db")
