from src.database.models import Base, engine, BreakingNews
try:
    BreakingNews.__table__.create(bind=engine)
    print("BreakingNews table created successfully.")
except Exception as e:
    print(f"Error creating table: {e}")

from sqlalchemy import inspect
inspector = inspect(engine)
print("Updated Tables in database:", inspector.get_table_names())
