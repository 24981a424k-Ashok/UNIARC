from src.database.models import SessionLocal, RawNews, VerifiedNews, DailyDigest
from sqlalchemy import desc

def check_twitter_status():
    db = SessionLocal()
    try:
        print("--- Twitter Status Diagnostic ---")
        
        # Latest RawNews from Twitter
        latest_raw = db.query(RawNews).filter(RawNews.source_id.like("x-%")).order_by(desc(RawNews.collected_at)).first()
        if latest_raw:
            print(f"Latest RawNews (Twitter): ID={latest_raw.id}, Collected: {latest_raw.collected_at}, Title: {latest_raw.title[:50]}...")
        else:
            print("(!) No RawNews found from Twitter.")

        # Latest VerifiedNews from Twitter
        latest_verified = db.query(VerifiedNews).filter(VerifiedNews.category == "Twitter 𝕏").order_by(desc(VerifiedNews.created_at)).first()
        if latest_verified:
            print(f"Latest VerifiedNews (Twitter): ID={latest_verified.id}, Created: {latest_verified.created_at}, Title: {latest_verified.title[:50]}...")
        else:
            print("(!) No VerifiedNews found from Twitter.")

        # Latest DailyDigest
        latest_digest = db.query(DailyDigest).order_by(desc(DailyDigest.date)).first()
        if latest_digest:
            generated_at = latest_digest.content_json.get('generated_at', 'Unknown')
            twitter_count = len(latest_digest.content_json.get('twitter_intelligence', []))
            print(f"Latest DailyDigest: Date={latest_digest.date}, Generated At: {generated_at}, Twitter Items: {twitter_count}")
        else:
            print("(!) No DailyDigest found.")

    finally:
        db.close()

if __name__ == "__main__":
    check_twitter_status()
