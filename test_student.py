import sys
import os
sys.path.append(os.getcwd())
import json
import re
from src.database.models import SessionLocal, VerifiedNews
from src.analysis.student_classifier import StudentClassifier

classifier = StudentClassifier()
db = SessionLocal()

articles = db.query(VerifiedNews).filter(VerifiedNews.country == 'in').order_by(VerifiedNews.created_at.desc()).limit(200).all()

print("Scanning 200 India Articles:")
count = 0
for a in articles:
    combined = f"{a.title} {a.content}".lower()
    
    # Check STRICT_KEYWORDS manually so we can print what matched
    strict_match = []
    for kw in classifier.STRICT_KEYWORDS:
        if re.search(rf'\b{kw}\b', combined, re.IGNORECASE):
            strict_match.append(kw)
    
    if not strict_match and not classifier._extract_specific_exam(combined):
        continue
        
    data = classifier.process_article(a.title, a.content)
    if not data:
        continue
        
    cat = data['category']
    count += 1
    
    # Find matching keywords for the assigned category
    cat_matches = []
    for kw in classifier.CATEGORIES.get(cat, []):
        if re.search(rf'\b{kw}\b', combined, re.IGNORECASE):
            cat_matches.append(kw)
            
    print(f"\n[{cat}] Title: {a.title}")
    print(f"URL: {a.url if hasattr(a, 'url') else 'N/A'}")
    print(f"Strict Match: {strict_match}")
    print(f"Cat Match: {cat_matches}")

print(f"\nTotal Student Articles: {count}")
