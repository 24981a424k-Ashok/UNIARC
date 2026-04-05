import sys
import os
from sqlalchemy import inspect
from loguru import logger

# Ensure src is in path
sys.path.append(os.getcwd())

try:
    from src.database.models import engine, Base
except ImportError:
    print("Error: Could not import models. Run from the project root.")
    sys.exit(1)

def audit_database():
    """
    Compares the current database schema with the SQLAlchemy models.
    Identifies missing tables or columns.
    """
    logger.info("Starting Comprehensive Database Audit...")
    inspector = inspect(engine)
    db_tables = inspector.get_table_names()
    
    mismatches = []
    
    for table_name, table_obj in Base.metadata.tables.items():
        model_cols = [c.name for c in table_obj.columns]
        
        if table_name in db_tables:
            db_cols = [c['name'] for c in inspector.get_columns(table_name)]
            missing = set(model_cols) - set(db_cols)
            if missing:
                mismatches.append(f"❌ Table '{table_name}' is MISSING columns: {missing}")
            else:
                logger.debug(f"✅ Table '{table_name}' matches model.")
        else:
            mismatches.append(f"❌ Table '{table_name}' is MISSING from the database.")

    if not mismatches:
        logger.info("🏆 SUCCESS: All database tables and columns match the models exactly.")
        print("\n[OK] Database schema is 100% aligned with models.")
    else:
        logger.error(f"🚨 FOUND {len(mismatches)} SCHEMA MISMATCHES:")
        for m in mismatches:
            print(m)
        print("\n[ERROR] Database schema is OUT OF SYNC. Please run migrations.")
        sys.exit(1)

if __name__ == "__main__":
    audit_database()
