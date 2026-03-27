import asyncio
from src.database.models import Base, engine, SessionLocal, BreakingNews
from src.scheduler.task_scheduler import run_news_cycle
from sqlalchemy import inspect

async def main():
    print(f"Using engine: {engine.url}")
    
    # Ensure table exists
    inspector = inspect(engine)
    if 'breaking_news' not in inspector.get_table_names():
        print("Table 'breaking_news' missing. Creating it now...")
        BreakingNews.__table__.create(bind=engine)
        print("Table created.")
    else:
        print("Table 'breaking_news' already exists.")
    
    print("\nStarting news cycle...")
    await run_news_cycle()
    print("\nNews cycle finished.")
    
    # Verify content
    db = SessionLocal()
    count = db.query(BreakingNews).count()
    print(f"Breaking News count in DB: {count}")
    db.close()

if __name__ == "__main__":
    asyncio.run(main())
