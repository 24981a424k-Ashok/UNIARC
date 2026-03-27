from src.database.models import SessionLocal, VerifiedNews
from sqlalchemy import or_
import json

def debug_query(q_str="", interests_str="Defense & Security"):
    db = SessionLocal()
    try:
        query = db.query(VerifiedNews)
        
        if q_str:
            query = query.filter(
                or_(
                    VerifiedNews.title.ilike(f"%{q_str}%"),
                    VerifiedNews.why_it_matters.ilike(f"%{q_str}%")
                )
            )
        
        if interests_str:
            interest_list = [i.strip() for i in interests_str.split(',')]
            interest_filters = [VerifiedNews.category.ilike(f"%{i}%") for i in interest_list]
            query = query.filter(or_(*interest_filters))
            
        # Print the SQL
        print("SQL Query:")
        print(query.statement.compile(compile_kwargs={"literal_binds": True}))
        
        articles = query.order_by(VerifiedNews.impact_score.desc(), VerifiedNews.created_at.desc()).limit(12).all()
        print(f"\nFound {len(articles)} articles.")
        for a in articles:
            print(f"- [{a.category}] {a.title} (Impact: {a.impact_score}, Created: {a.created_at})")
            
    finally:
        db.close()

if __name__ == "__main__":
    debug_query()
