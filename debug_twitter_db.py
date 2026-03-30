from src.database.models import SessionLocal, RawNews, VerifiedNews
from datetime import datetime
import pandas as pd

db = SessionLocal()
try:
    print("--- Latest Raw Twitter News ---")
    raw_tweets = db.query(RawNews).filter(RawNews.source_id.like("x-%")).order_by(RawNews.collected_at.desc()).limit(10).all()
    for t in raw_tweets:
        print(f"ID: {t.id}, Collected At: {t.collected_at}, Published At: {t.published_at}, Title: {t.title[:50]}")
    
    print("\n--- Latest Verified Twitter News ---")
    verified_tweets = db.query(VerifiedNews).filter(VerifiedNews.category == "Twitter 𝕏").order_by(VerifiedNews.created_at.desc()).limit(10).all()
    for v in verified_tweets:
        print(f"ID: {v.id}, Created At: {v.created_at}, Published At: {v.published_at}, Title: {v.title[:50]}")
finally:
    db.close()
