
import sys
import os
sys.path.append(os.getcwd())

from src.database.models import SessionLocal, VerifiedNews, DailyDigest
from sqlalchemy import func

def inspect_regional_data():
    db = SessionLocal()
    with open("inspection_results.log", "w", encoding="utf-8") as f:
        try:
            # Check VerifiedNews counts by country
            f.write("--- VerifiedNews counts by country ---\n")
            counts = db.query(VerifiedNews.country, func.count(VerifiedNews.id)).group_by(VerifiedNews.country).all()
            for country, count in counts:
                f.write(f"{country}: {count}\n")
            
            # Check specifically for China and UAE
            china_news = db.query(VerifiedNews).filter(VerifiedNews.country.in_(['China', 'cn', 'CN'])).limit(5).all()
            f.write(f"\nSample China news: {len(china_news)} items found\n")
            for n in china_news:
                f.write(f"- {n.title} (Country: {n.country})\n")
                
            uae_news = db.query(VerifiedNews).filter(VerifiedNews.country.in_(['UAE', 'ae', 'AE'])).limit(5).all()
            f.write(f"\nSample UAE news: {len(uae_news)} items found\n")
            for n in uae_news:
                f.write(f"- {n.title} (Country: {n.country})\n")
                
            # Check latest DailyDigest
            latest_digest = db.query(DailyDigest).filter(DailyDigest.is_published == True).order_by(DailyDigest.date.desc()).first()
            if latest_digest:
                f.write(f"\nLatest Digest Date: {latest_digest.date}\n")
                content = latest_digest.content_json
                countries = content.get("countries", {})
                f.write(f"Countries in digest: {list(countries.keys())}\n")
                
                for country_key in ["China", "cn", "UAE", "ae"]:
                    stories = countries.get(country_key, [])
                    f.write(f"- Stories in digest for '{country_key}': {len(stories)}\n")
            else:
                f.write("\nNo published digest found.\n")
                
        finally:
            db.close()
    print("Inspection complete. Results written to inspection_results.log")

if __name__ == "__main__":
    inspect_regional_data()
