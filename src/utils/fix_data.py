import sys
import os
import logging
from datetime import datetime

# Ensure src is in path
sys.path.append(os.getcwd())

from src.database.models import SessionLocal, BreakingNews, VerifiedNews
from sqlalchemy import func

# Configure Logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def fix_data():
    session = SessionLocal()
    try:
        # 1. Fix Repetition (Deduplication) FIRST
        logger.info("Checking for duplicates...")
        unique_titles = set()
        items_to_delete = []
        
        # We iterate and keep the *first* (newest by ID desc) one we see
        all_items_dedupe = session.query(BreakingNews).order_by(BreakingNews.id.desc()).all()
        
        for item in all_items_dedupe:
            title = item.breaking_headline or ""
            if title in unique_titles:
                items_to_delete.append(item.id)
            else:
                unique_titles.add(title)
                
        if items_to_delete:
            logger.info(f"Found {len(items_to_delete)} duplicates to delete.")
            session.query(BreakingNews).filter(BreakingNews.id.in_(items_to_delete)).delete(synchronize_session='fetch')
            session.flush() # Sync with DB
        else:
            logger.info("No duplicates found.")

        # 2. Fix "0 min ago" (recency_minutes)
        logger.info("Fixing timestamps...")
        # Re-fetch remaining items after deduplication
        remaining_items = session.query(BreakingNews).all()
        updated_count = 0
        
        for item in remaining_items:
            ref_time = item.created_at
            if item.verified_news and item.verified_news.published_at:
                ref_time = item.verified_news.published_at
            
            if ref_time:
                delta = datetime.utcnow() - ref_time
                minutes = int(delta.total_seconds() / 60)
                if minutes < 0: minutes = 0
                
                if item.recency_minutes == 0 or item.recency_minutes != minutes:
                    item.recency_minutes = minutes
                    updated_count += 1

        logger.info(f"Updated timestamps for {updated_count} items.")
        session.commit()
        logger.info("Database fix complete.")
        
    except Exception as e:
        session.rollback()
        logger.error(f"Error fixing data: {e}")
    finally:
        session.close()

if __name__ == "__main__":
    fix_data()
