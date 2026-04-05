import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

def test_dsns():
    raw_url = os.getenv("DATABASE_URL")
    print(f"Testing URL: {raw_url.split('@')[-1] if raw_url else 'None'} (Password masked)")
    
    # Mode 1: URL as is
    try:
        print("\n--- Testing Mode 1: psycopg2.connect(raw_url) ---")
        # Remove driver prefix for psycopg2.connect
        dsn = raw_url.replace("postgresql+psycopg2://", "postgresql://")
        conn = psycopg2.connect(dsn)
        print("Success!")
        conn.close()
    except Exception as e:
        print(f"Failed: {e}")

    # Mode 2: Keyword args (The most robust way)
    try:
        print("\n--- Testing Mode 2: psycopg2.connect(with kwargs) ---")
        # Manually parse for testing
        # postgresql://user:pass@host:port/db
        import re
        match = re.match(r'postgresql(?:\+psycopg2)?://([^:]+):([^@]+)@([^:/]+):(\d+)/(.+)', raw_url)
        if match:
            user, pw, host, port, db = match.groups()
            conn = psycopg2.connect(
                user=user,
                password=pw,
                host=host,
                port=port,
                database=db,
                sslmode='require'
            )
            print("Success!")
            conn.close()
        else:
            print("Failed to parse URL for kwargs test.")
    except Exception as e:
        print(f"Failed: {e}")

    # Mode 3: Supabase Fix (prepare_threshold=0)
    try:
        print("\n--- Testing Mode 3: psycopg2.connect(with prepare_threshold=0) ---")
        if match:
            user, pw, host, port, db = match.groups()
            conn = psycopg2.connect(
                user=user,
                password=pw,
                host=host,
                port=port,
                database=db,
                sslmode='require',
                prepare_threshold=0
            )
            print("Success!")
            conn.close()
    except Exception as e:
        print(f"Failed: {e}")

if __name__ == "__main__":
    test_dsns()
