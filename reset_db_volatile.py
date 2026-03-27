from src.database.models import Base, engine
from sqlalchemy import text, inspect

def reset_volatile_tables():
    print(f"Connecting to: {engine.url}")
    inspector = inspect(engine)
    tables_to_drop = [
        "breaking_news",
        "saved_articles",
        "read_history",
        "verified_news",
        "daily_digests"
    ]
    
    with engine.connect() as conn:
        for table in tables_to_drop:
            if table in inspector.get_table_names():
                print(f"Dropping {table}...")
                conn.execute(text(f"DROP TABLE {table}"))
        conn.commit()
    
    print("Creating tables with current schema...")
    Base.metadata.create_all(bind=engine)
    print("Verification: Tables now in DB:", inspect(engine).get_table_names())

if __name__ == "__main__":
    reset_volatile_tables()
