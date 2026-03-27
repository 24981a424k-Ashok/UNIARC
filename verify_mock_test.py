import sys
import os

# Add src to path
sys.path.append(os.getcwd())

from src.analysis.exam_generator import ExamGenerator
from src.database.models import SessionLocal

def test_gen():
    gen = ExamGenerator()
    db = SessionLocal()
    try:
        print("Testing Mock Test Generation...")
        # Force a context where it might use the bank
        # (e.g. by passing items that might fail LLM or just relying on the code flow)
        result = gen.generate_mock_test(db)
        
        print(f"Title: {result.get('title')}")
        questions = result.get('questions', [])
        print(f"Number of questions: {len(questions)}")
        
        if questions:
            for q in questions[:3]:
                print(f"- [{q.get('section')}] {q.get('question')[:50]}...")
        else:
            print("No questions generated!")
            
    finally:
        db.close()

if __name__ == "__main__":
    test_gen()
