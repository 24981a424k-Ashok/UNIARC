from src.database.models import SessionLocal, BreakingNews, VerifiedNews
from datetime import datetime

def insert_dummy():
    db = SessionLocal()
    try:
        # Get one verified news as base
        news = db.query(VerifiedNews).first()
        if not news:
            print("No verified news to link dummy breaking news to.")
            return
        
        dummy = BreakingNews(
            verified_news_id=news.id,
            classification="Breaking News",
            breaking_headline="TEST BREAKING NEWS SYSTEM",
            what_happened=["This is a dummy item added for debugging.", "If you see this, the system is working."],
            why_matters="Verification of end-to-end breaking news pipeline.",
            next_updates=["Wait for real news."],
            confidence_level="High",
            impact_score=9,
            recency_minutes=1,
            url="https://example.com",
            created_at=datetime.utcnow()
        )
        db.add(dummy)
        db.commit()
        print(f"Dummy breaking news inserted for news ID: {news.id}")
        
    except Exception as e:
        print(f"Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    insert_dummy()
