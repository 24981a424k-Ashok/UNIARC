from src.database.models import SessionLocal, RawNews, VerifiedNews, DailyDigest
from sqlalchemy import text

def reset_news_state():
    db = SessionLocal()
    try:
        print("Resetting database state to force fresh news cycle...")
        
        # Option 1: Delete all digests to force new generation
        deleted = db.query(DailyDigest).delete()
        print(f"Deleted {deleted} old digests.")
        
        # Option 2: Mark recent raw news as unprocessed (optional, if we want to re-analyze)
        # updated = db.query(RawNews).update({RawNews.processed: False})
        # print(f"Marked {updated} articles as unprocessed.")
        
        # Option 3: Nuke everything (Extreme, but ensures "New News")
        db.query(VerifiedNews).delete()
        db.query(RawNews).delete()
        print("Cleared all news articles.")
        
        db.commit()
        print("Reset complete. Running cycle will now generate a fresh digest.")
        
    except Exception as e:
        print(f"Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    reset_news_state()
