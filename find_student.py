import sys
import os
sys.path.append(os.getcwd())
from src.database.models import SessionLocal, VerifiedNews
from src.analysis.student_classifier import StudentClassifier

db = SessionLocal()
articles = db.query(VerifiedNews).order_by(VerifiedNews.published_at.desc()).limit(300).all()

classifier = StudentClassifier()
print(f"Scanning {len(articles)} articles for student keywords...")

missed = []
for a in articles:
    text = f"{a.title} {a.content}".lower()
    
    # Is it actually related to students?
    has_student_context = any(w in text for w in ["student", "exam", "university", "scholarship", "internship", "cbse", "nta"])
    
    if has_student_context:
        student_data = classifier.process_article(a.title, a.content)
        if not student_data:
            missed.append((a.title, a.source_name))

print(f"Found {len(missed)} articles that MIGHT be student-related but were blocked.")
for title, source in missed[:15]:
    print(f"- {title} ({source})")
