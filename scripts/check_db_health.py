import sys
import os
from pathlib import Path

# Add project root to sys.path
sys.path.append(str(Path(__file__).resolve().parent.parent))

from src.database.models import SessionLocal, RawNews, VerifiedNews, init_db
from sqlalchemy import text

def check_health():
    print("Checking Database Connection & Schema...")
    # Ensure tables exist
    init_db()
    print("Tables Initialized.")
    
    session = SessionLocal()
    try:
        # 1. Basic Connection Test
        res = session.execute(text("SELECT 1")).fetchone()
        print(f"Connection Successful! (Result: {res[0]})")
        
        # 2. Query Counts
        raw_count = session.query(RawNews).count()
        verified_count = session.query(VerifiedNews).count()
        print(f"Intelligence Node Status:")
        print(f" - Raw News Articles: {raw_count}")
        print(f" - Verified News Articles: {verified_count}")
        
    except Exception as e:
        print(f"DANGER: Database Connection Failed!")
        print(f"Error: {e}")
    finally:
        session.close()

if __name__ == "__main__":
    check_health()
