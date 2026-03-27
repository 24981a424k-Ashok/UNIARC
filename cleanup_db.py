"""
Database cleanup script
Removes old news articles to ensure fresh content
"""
from src.database.models import SessionLocal, RawNews, VerifiedNews, DailyDigest
from datetime import datetime, time

def cleanup_old_data():
    db = SessionLocal()
    
    try:
        # Target: 2026-01-28
        start_of_today = datetime(2026, 1, 28, 0, 0, 0)
        end_of_today = datetime(2026, 1, 28, 23, 59, 59)
        
        print("=" * 60)
        print(f"DATABASE CLEANUP: KEEPING ONLY 2026-01-28")
        print("=" * 60)

        # 1. Delete Daily Digests not from today
        digest_count = db.query(DailyDigest).filter(
            (DailyDigest.date < start_of_today) | (DailyDigest.date > end_of_today)
        ).delete(synchronize_session=False)
        
        # 2. Delete Verified News not from today
        verified_count = db.query(VerifiedNews).filter(
            (VerifiedNews.published_at < start_of_today) | (VerifiedNews.published_at > end_of_today)
        ).delete(synchronize_session=False)
            
        # 3. Delete Raw News not from today
        raw_count = db.query(RawNews).filter(
            (RawNews.published_at < start_of_today) | (RawNews.published_at > end_of_today)
        ).delete(synchronize_session=False)

        db.commit()
        
        print(f"\n✅ Deleted {digest_count} old digests")
        print(f"✅ Deleted {verified_count} old verified articles")
        print(f"✅ Deleted {raw_count} old raw articles")
        print("\nDatabase cleaned successfully! Only today's data remains.")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ Error during cleanup: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    cleanup_old_data()
