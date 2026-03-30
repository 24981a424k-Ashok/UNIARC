from src.database.models import SessionLocal, DailyDigest
import json

def check_digest():
    db = SessionLocal()
    try:
        latest = db.query(DailyDigest).order_by(DailyDigest.date.desc()).first()
        if not latest:
            print("No digest found.")
            return
        digest = db.query(DailyDigest).order_by(DailyDigest.date.desc()).first()
        if digest:
            print(f"Digest Date: {digest.date}")
            content = digest.content_json
            print(f"Has top_stories: {'top_stories' in content}")
            if 'top_stories' in content:
                print(f"Top Stories Count: {len(content['top_stories'])}")
            
            print(f"Has breaking_news: {'breaking_news' in content}")
            if 'breaking_news' in content:
                print(f"Breaking News Count: {len(content['breaking_news'])}")
                if len(content['breaking_news']) > 0:
                    print(f"First Breaking Headline: {content['breaking_news'][0].get('breaking_headline')}")
        else:
            print("No digest found.")
    finally:
        db.close()

if __name__ == "__main__":
    check_digest()
