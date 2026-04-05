from sqlalchemy import inspect
from src.database.models import engine, Base

def audit():
    inspector = inspect(engine)
    db_tables = inspector.get_table_names()
    
    mismatches = []
    print("Checking database for mismatches...")
    for table_name, table_obj in Base.metadata.tables.items():
        model_cols = [c.name for c in table_obj.columns]
        if table_name in db_tables:
            db_cols = [c['name'] for c in inspector.get_columns(table_name)]
            missing = set(model_cols) - set(db_cols)
            if missing:
                mismatches.append(f"Table {table_name} MISSING COLUMNS: {missing}")
        else:
            mismatches.append(f"Table {table_name} MISSING FROM DB")

    if not mismatches:
        print("ALL TABLES AND COLUMNS MATCH THE MODELS.")
    else:
        for m in mismatches:
            print(m)

if __name__ == "__main__":
    audit()
