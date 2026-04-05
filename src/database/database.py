import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# 1. Load environment first to ensure DATABASE_URL is available
load_dotenv()
DATA_DIR = os.getenv("DATA_DIR_PATH", "data")
DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{DATA_DIR}/news.db")

# 2. Setup Engine
if DATABASE_URL.startswith("sqlite"):
    engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
else:
    # Optimized for Direct Supabase/PostgreSQL Connection
    engine = create_engine(
        DATABASE_URL,
        pool_size=10,
        max_overflow=20,
        pool_timeout=30,
        pool_recycle=1800,
        pool_pre_ping=True,
        connect_args={
            "sslmode": "require"
        }
    )

# 3. Create Session Factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
