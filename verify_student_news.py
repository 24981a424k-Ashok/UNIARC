from src.database.models import SessionLocal, User, VerifiedNews
from src.delivery.web_dashboard import _update_student_cache_if_needed
from loguru import logger

def verify():
    db = SessionLocal()
    try:
        print("Testing _update_student_cache_if_needed...")
        # This will trigger the logic for 'Global' or the default country
        cache = _update_student_cache_if_needed(db, force=True, country="India")
        print("Success! No KeyError.")
        print(f"Total articles: {len(cache.get('articles', []))}")
        print(f"Categories found: {cache.get('trends', {}).get('category_counts', {}).keys()}")
    except Exception as e:
        print(f"Failure: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    verify()
