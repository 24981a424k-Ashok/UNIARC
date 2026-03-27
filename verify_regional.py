from src.database.models import SessionLocal, RawNews, VerifiedNews
from sqlalchemy import or_
import json

def verify_regional_intel():
    session = SessionLocal()
    try:
        print("=== Regional Intel Verification ===")
        
        # 1. Check for specialized country nodes
        countries_to_check = ['us', 'cn', 'gb', 'de', 'jp', 'sg', 'ae']
        for code in countries_to_check:
            count = session.query(RawNews).filter(RawNews.country == code).count()
            print(f"Node [{code.upper()}]: Found {count} raw articles")
            
        # 2. Check for specialized keywords in titles (sampling)
        special_keywords = {
            'us': ['stock', 'fed', 'corporate', 'ai', 'startup'],
            'cn': ['economy', 'trade', 'manufacturing', 'supply-chain'],
            'ae': ['energy', 'oil', 'mega', 'geopolitics'],
            'sg': ['fintech', 'asean']
        }
        
        print("\n=== Keyword Content Audit ===")
        for code, keywords in special_keywords.items():
            matches = []
            for kw in keywords:
                found = session.query(RawNews).filter(
                    RawNews.country == code,
                    or_(RawNews.title.like(f"%{kw}%"), RawNews.content.like(f"%{kw}%"))
                ).limit(2).all()
                if found:
                    matches.append(kw)
            print(f"Node [{code.upper()}]: Matches keywords {matches}")

        # 3. Check Latest Digest structure
        from src.database.models import DailyDigest
        latest = session.query(DailyDigest).order_by(DailyDigest.date.desc()).first()
        if latest:
            data = latest.content_json
            countries = data.get("countries", {})
            print(f"\n=== Dashboard Digest Audit (Date: {latest.date}) ===")
            print(f"Countries in Digest: {list(countries.keys())}")
            if "Singapore" in countries: print(f"✅ Singapore Node exists in Digest")
            if "UAE" in countries: print(f"✅ UAE Node exists in Digest")
            
            breaking = data.get("breaking_news", [])
            print(f"Breaking News Volume: {len(breaking)} (Target: up to 150)")
        else:
            print("\n❌ No DailyDigest found. Please run a news cycle (python main.py).")

    finally:
        session.close()

if __name__ == "__main__":
    verify_regional_intel()
