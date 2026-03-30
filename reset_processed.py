from src.database.models import SessionLocal, RawNews, VerifiedNews
from sqlalchemy import text

def reset_raw_news():
    db = SessionLocal()
    try:
        print("Resetting 'processed' status in raw_news...")
        db.execute(text("UPDATE raw_news SET processed = 0"))
        db.commit()
        
        count = db.query(RawNews).filter(RawNews.processed == False).count()
        print(f"Total unprocessed raw news: {count}")
        
    finally:
        db.close()

if __name__ == "__main__":
    reset_raw_news()
