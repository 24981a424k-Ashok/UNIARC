import requests
import sqlite3
import os

PORT = 8000
BASE_URL = f"http://localhost:{PORT}"
DB_PATH = os.path.join("data", "news.db")

def check_endpoint(url, description):
    try:
        response = requests.get(url)
        print(f"[{response.status_code}] {description}: {url}")
        return response
    except Exception as e:
        print(f"[FAIL] {description}: {e}")
        return None

def check_db():
    if not os.path.exists(DB_PATH):
        print(f"[FAIL] Database not found at {DB_PATH}")
        return

    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Check DailyDigest
        cursor.execute("SELECT count(*) FROM daily_digests")
        count = cursor.fetchone()[0]
        print(f"[DB] daily_digests count: {count}")
        
        # Check recent digest
        cursor.execute("SELECT date, is_published FROM daily_digests ORDER BY date DESC LIMIT 1")
        row = cursor.fetchone()
        if row:
            print(f"[DB] Latest digest: Date={row[0]}, Published={row[1]}")
        else:
            print("[DB] No digests found.")

        # Check raw_news
        cursor.execute("SELECT count(*) FROM raw_news")
        raw_count = cursor.fetchone()[0]
        print(f"[DB] raw_news count: {raw_count}")

        conn.close()
    except Exception as e:
        print(f"[DB] Error checking database: {e}")

def main():
    print("--- STARTING FEATURE VERIFICATION ---")
    
    # 1. Health Check
    check_endpoint(f"{BASE_URL}/health", "Health Check")
    
    # 2. Dashboard
    resp = check_endpoint(f"{BASE_URL}/dashboard", "Dashboard")
    if resp and resp.status_code == 200:
        if "System Initializing" in resp.text:
            print("[WARN] Dashboard shows 'System Initializing'")
        else:
            print("[OK] Dashboard loaded (content length: " + str(len(resp.text)) + ")")
            
    # 3. Business Intel
    resp = check_endpoint(f"{BASE_URL}/business-intelligence", "Business Intel")
    
    # 4. Breaking News API
    check_endpoint(f"{BASE_URL}/api/breaking-news", "Breaking News API")

    # 5. Database Check
    check_db()

    print("--- VERIFICATION COMPLETE ---")

if __name__ == "__main__":
    main()
