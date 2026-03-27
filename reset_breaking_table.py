from src.database.models import Base, engine, BreakingNews
from sqlalchemy import text, inspect

def reset_breaking_table():
    print(f"Connecting to: {engine.url}")
    inspector = inspect(engine)
    
    if 'breaking_news' in inspector.get_table_names():
        print("Dropping existing breaking_news table...")
        with engine.connect() as conn:
            conn.execute(text("DROP TABLE breaking_news"))
            conn.commit()
    
    print("Creating breaking_news table with current schema...")
    BreakingNews.__table__.create(bind=engine)
    print("Verification: Tables now in DB:", inspect(engine).get_table_names())

if __name__ == "__main__":
    reset_breaking_table()
