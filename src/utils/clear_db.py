import sys
import os
from loguru import logger

# Ensure src is in path
sys.path.append(os.getcwd())

from src.database.models import SessionLocal, RawNews, VerifiedNews, DailyDigest, BreakingNews, OTPVerification

def clear_news_data():
    """Truncate or delete all news-related records for a fresh start."""
    session = SessionLocal()
    try:
        logger.info("Initializing Data Wipe (News Intelligence Only)...")
        
        # Order matters for foreign keys
        logger.info("Cleaning Breaking News...")
        session.query(BreakingNews).delete()
        
        logger.info("Cleaning Daily Digests...")
        session.query(DailyDigest).delete()
        
        logger.info("Cleaning Verified Intelligence Nodes...")
        session.query(VerifiedNews).delete()
        
        logger.info("Cleaning Raw Ingested Headlines...")
        session.query(RawNews).delete()
        
        logger.info("Cleaning Old OTP Verification Records...")
        session.query(OTPVerification).delete()
        
        session.commit()
        logger.info("✅ Database Reset Complete. System is now empty and ready for a fresh cycle.")
        
    except Exception as e:
        session.rollback()
        logger.error(f"❌ Data Wipe Failed: {e}")
    finally:
        session.close()

if __name__ == "__main__":
    clear_news_data()
