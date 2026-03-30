from src.database.models import SessionLocal, RawNews
import json

def quick_audit():
    session = SessionLocal()
    try:
        # Check counts for all nodes including new ones
        nodes = ['us', 'cn', 'gb', 'de', 'jp', 'sg', 'ae', 'in']
        results = {}
        for node in nodes:
            count = session.query(RawNews).filter(RawNews.country == node).count()
            results[node] = count
            
        print("NEWS NODE COUNTS:")
        print(json.dumps(results, indent=2))
        
        # Check for specific "Must-Have" content
        # Example: US Fed/Stock
        us_intel = session.query(RawNews).filter(RawNews.country == 'us').limit(3).all()
        print("\nUSA INTEL SAMPLE:")
        for a in us_intel:
            print(f"- {a.title}")
            
        # Example: UAE Oil/Energy
        uae_intel = session.query(RawNews).filter(RawNews.country == 'ae').limit(3).all()
        print("\nUAE INTEL SAMPLE:")
        for a in uae_intel:
            print(f"- {a.title}")

    finally:
        session.close()

if __name__ == "__main__":
    quick_audit()
