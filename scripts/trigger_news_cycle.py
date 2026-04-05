import asyncio
import logging
import sys
from pathlib import Path

# Add project root to sys.path
sys.path.append(str(Path(__file__).resolve().parent.parent))

from src.scheduler.task_scheduler import run_news_cycle

async def main():
    # Configure logging to see output
    logging.basicConfig(level=logging.INFO)
    print("Triggering Manual News Collection Cycle...")
    await run_news_cycle()
    print("Cycle Complete.")

if __name__ == "__main__":
    asyncio.run(main())
