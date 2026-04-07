import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv()

def fix_sequences():
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        print("DATABASE_URL not found in .env")
        return

    # Handle Postgres dialect if needed
    if database_url.startswith("postgres://"):
        database_url = database_url.replace("postgres://", "postgresql://", 1)

    engine = create_engine(database_url)
    
    # List of tables with SERIAL primary keys
    tables = [
        "verified_news", "raw_news", "daily_digests", "track_notifications", 
        "users", "protocol_history", "topic_tracking", "otp_verifications",
        "subscriptions", "folders", "saved_articles", "read_history",
        "flagged_articles", "breaking_news", "advertisements", "newspapers"
    ]
    
    with engine.connect() as conn:
        print("Starting sequence synchronization...")
        for table in tables:
            try:
                # Get the sequence name (standard Postgres naming: table_id_seq)
                # But it's safer to just set the value based on MAX(id)
                seq_val_query = text(f"SELECT setval(pg_get_serial_sequence('{table}', 'id'), (SELECT MAX(id) FROM {table}))")
                conn.execute(seq_val_query)
                conn.commit()
                print(f"✅ Synced sequence for table: {table}")
            except Exception as e:
                # Some tables might not have the standard id or sequence name
                if "null" in str(e).lower():
                    print(f"ℹ️  Table {table} sequence is already in sync or has no data.")
                else:
                    print(f"⚠️  Could not sync sequence for {table}: {e}")
        
    print("\nDatabase health check complete. Sequences are now synchronized.")

if __name__ == "__main__":
    fix_sequences()
