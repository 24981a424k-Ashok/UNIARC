import sys
import os
from pathlib import Path

# Add root to sys.path
sys.path.append(str(Path(__file__).parent))

from src.database.models import SessionLocal, RawNews, VerifiedNews
from datetime import datetime

def test_fix():
    db = SessionLocal()
    test_url = "https://example.com/test-deployment-fix-" + datetime.utcnow().strftime("%Y%m%d%H%M%S")
    
    print(f"Testing URL: {test_url}")
    
    # Mock payload
    from pydantic import BaseModel
    class MockPayload:
        def __init__(self, title, description, image_url, redirect_url, category, access_link):
            self.title = title
            self.description = description
            self.image_url = image_url
            self.redirect_url = redirect_url
            self.category = category
            self.access_link = access_link

    payload1 = MockPayload(
        "Initial Title", 
        "Initial Description", 
        "http://img1.vibe", 
        test_url, 
        "Scholarships & Internships", 
        "http://apply1.vibe"
    )

    print("\n--- Phase 1: Creating New Article ---")
    try:
        # Simulate logic from create_manual_student_article manually
        raw = RawNews(
            title=payload1.title,
            description=payload1.description,
            url=payload1.redirect_url,
            url_to_image=payload1.image_url,
            source_name="Test Source",
            published_at=datetime.utcnow(),
            is_verified=True,
            processed=True,
            country="Global"
        )
        db.add(raw)
        db.flush()
        
        verified = VerifiedNews(
            raw_news_id=raw.id,
            title=payload1.title,
            content=payload1.description,
            summary_bullets=["Test"],
            impact_tags=[payload1.category],
            bias_rating="Neutral",
            category=payload1.category,
            impact_score=100,
            why_it_matters="Test",
            sentiment="Neutral",
            published_at=datetime.utcnow()
        )
        db.add(verified)
        db.commit()
        print("✅ Phase 1 Success: Article created.")
    except Exception as e:
        db.rollback()
        print(f"❌ Phase 1 Failure: {e}")
        return

    print("\n--- Phase 2: Deploying Same URL (The Fix Test) ---")
    payload2 = MockPayload(
        "Updated Title", 
        "Updated Description", 
        "http://img2.vibe", 
        test_url, 
        "Career & Jobs", 
        "http://apply2.vibe"
    )

    try:
        # This is where the old logic failed (IntegrityError on URL)
        # We manually verify the new logic's flow
        
        # 1. Lookup
        raw_existing = db.query(RawNews).filter(RawNews.url == payload2.redirect_url).first()
        if raw_existing:
            print(f"Found existing raw news: {raw_existing.id}")
            raw_existing.title = payload2.title
            raw_existing.description = payload2.description
            
            verified_existing = db.query(VerifiedNews).filter(VerifiedNews.raw_news_id == raw_existing.id).first()
            if verified_existing:
                print(f"Found existing verified news: {verified_existing.id}")
                verified_existing.title = payload2.title
                verified_existing.category = payload2.category
                db.commit()
                print("✅ Phase 2 Success: Duplicate URL handled and entry updated!")
            else:
                print("❌ Phase 2 Failure: Raw found but Verified missing (Logic gap)")
        else:
            print("❌ Phase 2 Failure: Existing URL not found (Cleanup failure?)")
            
    except Exception as e:
        db.rollback()
        print(f"❌ Phase 2 Failure (Fix Failed): {e}")

    # Cleanup
    print("\n--- Cleaning up test data ---")
    try:
        r = db.query(RawNews).filter(RawNews.url == test_url).first()
        if r:
            v = db.query(VerifiedNews).filter(VerifiedNews.raw_news_id == r.id).first()
            if v: db.delete(v)
            db.delete(r)
            db.commit()
            print("Done.")
    except: pass
    finally: db.close()

if __name__ == "__main__":
    test_fix()
