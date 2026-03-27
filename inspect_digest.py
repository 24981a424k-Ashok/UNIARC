from src.database.models import SessionLocal, DailyDigest
import json

def inspect_digest():
    db = SessionLocal()
    latest = db.query(DailyDigest).order_by(DailyDigest.date.desc()).first()
    if latest:
        print(f"Digest ID: {latest.id}")
        # Print a small subset of the JSON to avoid overwhelming output
        data = latest.content_json
        print(f"Keys: {list(data.keys())}")
        print(f"Top Story 0 Title: {data.get('top_stories', [{}])[0].get('title')}")
        print(f"Twitter Count: {len(data.get('twitter_intelligence', []))}")
        print(f"Generated At: {data.get('generated_at')}")
        
        first_story = data.get('top_stories', [{}])[0]
        print(f"First Story Full JSON:")
        print(json.dumps(first_story, indent=2))
        
        # Check specific fields that were null before
        null_fields = [k for k, v in first_story.items() if v is None]
        print(f"Null fields detected in first story: {null_fields}")
    else:
        print("No digest found.")
    db.close()

if __name__ == "__main__":
    inspect_digest()
