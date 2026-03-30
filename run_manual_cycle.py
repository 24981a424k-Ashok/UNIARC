import asyncio
from src.scheduler.task_scheduler import run_news_cycle

if __name__ == "__main__":
    print("Starting manual news cycle...")
    asyncio.run(run_news_cycle())
    print("Manual news cycle completed.")
