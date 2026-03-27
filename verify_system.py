"""
Pre-launch verification script
Checks news freshness and system health
"""
import os
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

from src.database.models import SessionLocal, RawNews, VerifiedNews, DailyDigest
from datetime import datetime, timedelta

def check_system():
    db = SessionLocal()
    
    try:
        # Check raw news
        total_raw = db.query(RawNews).count()
        cutoff = datetime.utcnow() - timedelta(hours=24)
        recent_raw = db.query(RawNews).filter(RawNews.published_at > cutoff).count()
        old_raw = total_raw - recent_raw
        
        # Check verified news
        total_verified = db.query(VerifiedNews).count()
        
        # Check digests
        total_digests = db.query(DailyDigest).count()
        latest_digest = db.query(DailyDigest).order_by(DailyDigest.date.desc()).first()
        
        print("=" * 60)
        print("SYSTEM HEALTH CHECK")
        print("=" * 60)
        print(f"\nRAW NEWS:")
        print(f"  Total articles: {total_raw}")
        print(f"  Recent (last 24h): {recent_raw}")
        print(f"  Old articles (>24h): {old_raw}")
        
        print(f"\nVERIFIED NEWS:")
        print(f"  Total verified: {total_verified}")
        
        print(f"\nDIGESTS:")
        print(f"  Total digests: {total_digests}")
        if latest_digest:
            print(f"  Latest digest date: {latest_digest.date}")
        
        print("\n" + "=" * 60)
        
        if recent_raw == 0:
            print("(!) WARNING: No recent news in last 24 hours!")
            print("   Run: python main.py run-once")
        else:
            print(f"(OK) System has {recent_raw} recent articles")
        
        if old_raw > 100:
            print(f"(!) WARNING: {old_raw} old articles in database")
            print("   Consider cleaning up old data")
        
        print("=" * 60)
        
    finally:
        db.close()

if __name__ == "__main__":
    import sys
    # Ensure UTF-8 output if possible
    if sys.platform == 'win32':
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    check_system()
