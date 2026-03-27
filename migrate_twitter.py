from src.database.models import SessionLocal, RawNews, VerifiedNews

def migrate():
    db = SessionLocal()
    try:
        twitter_raw = db.query(RawNews).filter(RawNews.source_id.like('x-%')).all()
        print(f"Processing {len(twitter_raw)} twitter articles...")
        count = 0
        for r in twitter_raw:
            existing = db.query(VerifiedNews).filter(VerifiedNews.raw_news_id == r.id).first()
            if not existing:
                v = VerifiedNews(
                    raw_news_id=r.id,
                    title=r.title,
                    content=r.content,
                    category="Twitter 𝕏",
                    summary_bullets=[r.title],
                    why_it_matters="Trending social update.",
                    impact_score=5,
                    credibility_score=0.9,
                    bias_rating="Neutral"
                )
                db.add(v)
                r.processed = True
                count += 1
        db.commit()
        print(f"Migration complete. Added {count} verified Twitter articles.")
    finally:
        db.close()

if __name__ == "__main__":
    migrate()
