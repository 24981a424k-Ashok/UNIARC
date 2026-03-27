import sys
from src.database.models import SessionLocal, DailyDigest

def test_business_mapping():
    db = SessionLocal()
    try:
        latest = db.query(DailyDigest).filter(DailyDigest.is_published == True).order_by(DailyDigest.date.desc()).first()
        if not latest:
            print("No digest found.")
            return

        data = latest.content_json
        categories = data.get("categories", {})
        
        # Simulation of the logic in web_dashboard.py
        category_request = "Business"
        normalized = category_request.lower().replace(" ", "_")
        
        category_map = {
            "business": "Business & Economy",
            "economy": "Business & Economy"
        }
        
        target_key = category_map.get(normalized, category_request)
        
        print(f"Request: {category_request}")
        print(f"Normalized: {normalized}")
        print(f"Mapped Target: {target_key}")
        
        if target_key in categories:
            print(f"SUCCESS: Found '{target_key}' in database with {len(categories[target_key])} items.")
        else:
            print(f"FAILURE: '{target_key}' not found in database keys: {list(categories.keys())}")

    except Exception as e:
        print(f"Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    test_business_mapping()
