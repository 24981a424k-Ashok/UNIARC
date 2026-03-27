from src.database.models import init_db
import logging

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    logging.info("Initializing Database...")
    init_db()
    logging.info("Database initialized successfully.")
