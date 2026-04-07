import asyncio
import logging
from src.scheduler.task_scheduler import run_news_cycle

logging.basicConfig(level=logging.INFO)

async def force_kickstart():
    print("🚀 Manually Force-Triggering News Intelligence Cycle...")
    await run_news_cycle()
    print("✅ Cycle Complete. Fresh news committed to database.")

if __name__ == "__main__":
    asyncio.run(force_kickstart())
