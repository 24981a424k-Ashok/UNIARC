from src.database.models import SessionLocal, VerifiedNews, RawNews
from datetime import datetime, timedelta
from src.database.models import engine
print(f"Connecting to database: {engine.url}")

def check_stats():
    db = SessionLocal()
    try:
        now = datetime.utcnow()
        last_24h = now - timedelta(hours=24)
        last_6h = now - timedelta(hours=6)
        
        verified_24h = db.query(VerifiedNews).filter(VerifiedNews.created_at >= last_24h).count()
        verified_6h = db.query(VerifiedNews).filter(VerifiedNews.created_at >= last_6h).count()
        
        raw_24h = db.query(RawNews).filter(RawNews.collected_at >= last_24h).count()
        raw_6h = db.query(RawNews).filter(RawNews.collected_at >= last_6h).count()
        
        from src.database.models import BreakingNews
        breaking_total = db.query(BreakingNews).count()
        breaking_24h = db.query(BreakingNews).filter(BreakingNews.created_at >= last_24h).count()
        
        print(f"Verified News (last 24h): {verified_24h}")
        print(f"Verified News (last 6h): {verified_6h}")
        print(f"Raw News (last 24h): {raw_24h}")
        print(f"Raw News (last 6h): {raw_6h}")
        print(f"Breaking News (Total): {breaking_total}")
        print(f"Breaking News (last 24h): {breaking_24h}")
        
    except Exception as e:
        import traceback
        print(f"Error in stats calculation: {e}")
        traceback.print_exc()
    finally:
        db.close()

if __name__ == "__main__":
    check_stats()
