from src.database.models import SessionLocal, VerifiedNews
from datetime import datetime, timedelta
from src.analysis.student_classifier import StudentClassifier

db = SessionLocal()
now = datetime.utcnow()
twenty_four_hours_ago = now - timedelta(days=30) # Check 30 days

raw_articles = db.query(VerifiedNews).filter(
    VerifiedNews.country == "in",
    VerifiedNews.created_at >= twenty_four_hours_ago
).all()

print(f"Total India articles in last 48 hours: {len(raw_articles)}")

classifier = StudentClassifier()
student_keywords = ["student", "exam", "school", "university", "college", "scholarship", "syllabus", "ugc", "cbse", "nta", "placement", "job", "career", "admission", "education", "study"]

passed_prefilter = 0
passed_classifier = 0

for article in raw_articles:
    combined = f"{article.title} {article.content}".lower()
    if any(k in combined for k in student_keywords):
        passed_prefilter += 1
        data = classifier.process_article(article.title, article.content)
        if data and data["category"] != "General Student News":
            passed_classifier += 1
            print(f"MATCH: {article.title} -> {data['category']}")

print(f"Passed Prefilter: {passed_prefilter}")
print(f"Passed Classifier (Categorized): {passed_classifier}")
