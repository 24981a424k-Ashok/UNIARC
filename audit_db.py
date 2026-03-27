from src.database.models import SessionLocal, VerifiedNews
from sqlalchemy import func

def audit_categories():
    db = SessionLocal()
    try:
        counts = db.query(VerifiedNews.category, func.count(VerifiedNews.id)).group_by(VerifiedNews.category).all()
        print("Category distribution in VerifiedNews:")
        for cat, count in counts:
            print(f"- {cat or 'None'}: {count}")
            
        total = db.query(VerifiedNews).count()
        print(f"\nTotal Verified Articles: {total}")
    finally:
        db.close()

if __name__ == "__main__":
    audit_categories()
