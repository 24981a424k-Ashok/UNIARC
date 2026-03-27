import sys, os
sys.path.append(os.getcwd())
from src.database.models import SessionLocal, VerifiedNews
from src.analysis.student_classifier import StudentClassifier
from datetime import datetime, timedelta

db = SessionLocal()
now = datetime.utcnow()
twenty_four_hours_ago = now - timedelta(hours=24)

raw_articles = db.query(VerifiedNews).filter(
    VerifiedNews.country == "in",
    VerifiedNews.created_at >= twenty_four_hours_ago
).order_by(VerifiedNews.created_at.desc()).limit(200).all()

print(f"Loaded {len(raw_articles)} India articles")

sc = StudentClassifier()
processed = []
for a in raw_articles:
    combined = f"{a.title} {a.content}".lower()
    if not any(kw in combined for kw in ["student", "exam", "school", "university", "college", "scholarship", "syllabus", "ugc", "cbse", "nta", "placement", "job", "career", "admission"]):
        continue
        
    sdata = sc.process_article(a.title, a.content)
    if sdata:
        processed.append(sdata)
    else:
        # Check if it was "NEET" and failed
        if "neet" in combined or "exam" in combined:
            print(f"FAILED process_article: {a.title}")

print(f"Total processed: {len(processed)}")
