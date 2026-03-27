import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
from loguru import logger

# Create a simplified app without lifespan for serverless
app = FastAPI(title="AI News Intelligence Agent")

# Import routes
try:
    from src.delivery.web_dashboard import router as dashboard_router
    from src.delivery.user_retention import router as retention_router
    app.include_router(retention_router, prefix="/api/retention")
    app.include_router(dashboard_router)
except Exception as e:
    logger.error(f"Error importing routers: {e}")

# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "healthy", "environment": "vercel"}

@app.get("/api/cron/process-news")
async def trigger_news_cycle():
    """Trigger the news processing cycle via Vercel Cron"""
    logger.info("Cron job triggered news cycle...")
    from src.scheduler.task_scheduler import run_news_cycle
    # We run it in a thread or just await if it was async, 
    # but run_news_cycle is synchronous logic currently.
    await run_news_cycle()
    return JSONResponse(content={"status": "success", "message": "News cycle completed"}, status_code=200)

@app.get("/")
async def root():
    return {"message": "AI News Intelligence Agent API", "status": "running"}

# Vercel serverless function handler
handler = app
