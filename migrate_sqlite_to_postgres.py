import sys
import os
from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import sessionmaker
from loguru import logger

# Ensure src is in path
if os.getcwd() not in sys.path:
    sys.path.append(os.getcwd())

from src.database.models import Base, RawNews, VerifiedNews, DailyDigest, BreakingNews, User, TopicTracking, TopicTracking, TrackNotification, Newspaper

# CONFIGURATION
SQLITE_URL = "sqlite:///data/news.db"
# Use the Postgres URL from .env or override here
POSTGRES_URL = "postgresql://postgres.npabvnvlzljonmlvwxev:rsqNeWkY5Ie4ZZyy@aws-1-ap-northeast-2.pooler.supabase.com:6543/postgres"

def migrate():
    logger.info("🚀 Starting Zero-Loss Migration: SQLite -> PostgreSQL")

    # 1. Setup Engines
    sqlite_engine = create_engine(SQLITE_URL)
    postgres_engine = create_engine(POSTGRES_URL)

    # 2. Create Schema in Postgres
    logger.info("Initializing Fresh Schema in PostgreSQL (dropping old if exists)...")
    Base.metadata.drop_all(bind=postgres_engine)
    Base.metadata.create_all(bind=postgres_engine)

    # 3. Setup Sessions
    SqliteSession = sessionmaker(bind=sqlite_engine)
    PostgresSession = sessionmaker(bind=postgres_engine)

    sqlite_db = SqliteSession()
    postgres_db = PostgresSession()

    try:
        # Tables to migrate in order (dependencies first)
        tables = [
            (User, "users"),
            (RawNews, "raw_news"),
            (VerifiedNews, "verified_news"),
            (BreakingNews, "breaking_news"),
            (DailyDigest, "daily_digests"),
            (Newspaper, "newspapers"),
            (TopicTracking, "topic_tracking"),
            (TrackNotification, "track_notifications")
        ]

        for model, name in tables:
            logger.info(f"Migrating table: {name}...")
            
            # Clear existing data in Postgres for this table to avoid duplicates during migration
            # (Only if the user wants a clean replacement, which they do "remove old data" + "work like now")
            # postgres_db.query(model).delete()
            
            # Fetch all from SQLite
            items = sqlite_db.query(model).all()
            if not items:
                logger.info(f"Table {name} is empty. Skipping.")
                continue

            logger.info(f"Found {len(items)} items in {name}. Transferring...")
            
            # Convert to dict and strip state, then add to Postgres
            # We use make_transient to detach from sqlite session
            from sqlalchemy.orm import make_transient
            
            count = 0
            for item in items:
                sqlite_db.expunge(item)
                make_transient(item)
                postgres_db.add(item)
                count += 1
                if count % 100 == 0:
                    postgres_db.commit()
                    logger.info(f"Progress: {count}/{len(items)}...")
            
            postgres_db.commit()
            logger.info(f"✅ Successfully migrated {len(items)} items to {name}.")

        logger.info("✨ MIGRATION COMPLETE! All data transferred perfectly.")

    except Exception as e:
        logger.error(f"❌ Migration Failed: {e}")
        postgres_db.rollback()
        raise e
    finally:
        sqlite_db.close()
        postgres_db.close()

if __name__ == "__main__":
    migrate()
