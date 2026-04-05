import os
# Suppress TensorFlow oneDNN info logs
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2' # Also suppress general TF info/warning logs

import sys
import asyncio
import logging

# Ensure src is in path for imports
if os.getcwd() not in sys.path:
    sys.path.append(os.getcwd())

import uvicorn
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, Response
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import FileResponse
from starlette.responses import JSONResponse
from loguru import logger
import sys

# Silence noisy external libraries
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("openai").setLevel(logging.WARNING)
logging.getLogger("httpcore").setLevel(logging.WARNING)
logging.getLogger("urllib3").setLevel(logging.CRITICAL)

from src.config import settings
from src.scheduler.task_scheduler import start_scheduler

from src.delivery.web_dashboard import router as dashboard_router
from src.delivery.user_retention import router as retention_router

# Configure logging
try:
    log_dir = os.path.join("data", "logs")
    os.makedirs(log_dir, exist_ok=True)
    logger.add(os.path.join(log_dir, "app.log"), rotation="500 MB", level="INFO")
except Exception as e:
    # If file logging fails (e.g. read-only filesystem), we fall back to stderr (default)
    # The default loguru handler is already added to stderr
    print(f"File logging disabled due to error: {e}")

from src.database.models import init_db

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Starting AI News Intelligence Agent...")

    # Environment Check (Checking through SecretManager which handles DB + Env)
    from src.utils.secret_manager import SecretManager
    
    required_keys = ["OPENAI_API_KEY", "NEWS_API_KEY"]
    missing_keys = [key for key in required_keys if not SecretManager.get(key)]
    if missing_keys:
        logger.warning(f"⚠️  MISSING CRITICAL KEYS: {', '.join(missing_keys)}. Analysis and collection may fail or use mocks.")
    
    if not SecretManager.get("FIREBASE_SERVICE_ACCOUNT_JSON") and not os.path.exists("service-account.json") and not SecretManager.get("FIREBASE_PRIVATE_KEY"):
         logger.warning("⚠️  No Firebase credentials found (DB, ENV, or file). Database/App sync might fail.")
    
    # Initialize DB
    init_db()
    logger.info("Database initialized.")

    # Initialize Firebase
    from src.config.firebase_config import initialize_firebase
    initialize_firebase()
    
    # Background startup tasks to avoid blocking health checks
    def _background_startup_tasks():
        # 1. Auto-seed Newspapers if empty
        try:
            from seed_newspapers import seed_newspapers
            seed_newspapers()
        except Exception as e:
            logger.error(f"Newspaper seeding failed: {e}")
        
        # 2. Run one-time data fix
        try:
            from src.utils.fix_data import fix_data
            logger.info("Running one-time data fix (timestamps & deduplication)...")
            fix_data()
        except Exception as e:
            logger.error(f"Data fix failed: {e}")
            
        # 3. Auto-trigger news cycle if DB is empty
        from src.database.models import SessionLocal, VerifiedNews
        db = SessionLocal()
        try:
            if db.query(VerifiedNews).count() == 0:
                logger.info("🥶 Cold Start Detected: Triggering immediate background news cycle...")
                import asyncio
                from src.scheduler.task_scheduler import run_news_cycle
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                import time
                time.sleep(3)
                loop.run_until_complete(run_news_cycle())
                loop.close()
            else:
                logger.info("✅ Database has data. Waiting for scheduled cycle.")
        except Exception as e:
            logger.error(f"Failed to auto-trigger news cycle: {e}")
        finally:
            db.close()

    # 4. Self-Healing: Sync DB Sequences (Fixes Duplicate Key Error)
    try:
        from src.database.models import engine, text
        with engine.connect() as conn:
            logger.info("Synchronizing database sequences (Self-Healing)...")
            tables = ["verified_news", "raw_news", "daily_digests", "notifications", "subscriber_profiles", "protocol_history"]
            for table in tables:
                try:
                    conn.execute(text(f"SELECT setval(pg_get_serial_sequence('{table}', 'id'), (SELECT MAX(id) FROM {table}))"))
                    conn.commit()
                except: continue
            logger.info("✅ Database sequences synchronized.")
    except Exception as e:
        logger.error(f"Sequence sync failed: {e}")

    import threading
    threading.Thread(target=_background_startup_tasks, daemon=True).start()
    
    # Start Scheduler
    scheduler = start_scheduler()
    logger.info("Scheduler started.")

    yield
    
    # Shutdown
    logger.info("Shutting down...")
    if scheduler:
        scheduler.shutdown()

app = FastAPI(title="AI News Intelligence Agent", lifespan=lifespan)

# Mount static files
app.mount("/static", StaticFiles(directory="web/static"), name="static")

# Include Routers
app.include_router(retention_router)
app.include_router(dashboard_router)

@app.get("/favicon.ico", include_in_schema=False)
async def favicon():
    return FileResponse("web/static/favicon.png")

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

def main():
    if len(sys.argv) > 1:
        command = sys.argv[1]
        if command == "run-once":
            logger.info("Running manual news cycle...")
            from src.scheduler.task_scheduler import run_news_cycle
            import asyncio
            asyncio.run(run_news_cycle())
        elif command == "run-twitter":
            logger.info("Running manual Twitter cycle (with Digest Update)...")
            from src.scheduler.task_scheduler import run_twitter_only_cycle
            import asyncio
            asyncio.run(run_twitter_only_cycle())
            logger.info("Manual Twitter cycle complete.")
        elif command == "init-db":
             from src.utils.init_db import init_db
             init_db()
        else:
            logger.error(f"Unknown command: {command}")
    else:
        # Run Web Server
        port = int(os.environ.get("PORT", 7860))
        logger.info(f"🚀 Launching server on port {port}...")
        # IMPORTANT: Bind to 0.0.0.0 for Hugging Face Spaces compatibility
        uvicorn.run("main:app", host="0.0.0.0", port=port, reload=False)

if __name__ == "__main__":
    main()
