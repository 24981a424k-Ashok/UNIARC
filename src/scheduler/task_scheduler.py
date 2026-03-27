import time
from typing import List, Dict, Any
# import logging
from apscheduler.schedulers.background import BackgroundScheduler
from sqlalchemy.orm import Session

from src.config.settings import SCHEDULE_TIME
from src.database.models import SessionLocal, RawNews
from src.collectors.news_api import NewsCollector
from src.collectors.twitter_collector import TwitterCollector
from src.verification.verifier import VerificationEngine
from src.collectors.social_media_collector import SocialMediaCollector
from src.analysis.llm_analyzer import LLMAnalyzer
from src.digest.generator import DigestGenerator
from src.database.models import SessionLocal, RawNews, VerifiedNews
from src.delivery.notifications import NotificationManager

from loguru import logger

async def run_news_cycle():
    logger.info("Starting Daily News Cycle...")
    db = SessionLocal()
    
    try:
        # 1. Collect
        logger.info("Step 1: Collection")
        
        api_count = rss_count = twitter_count = trending_count = gnews_count = 0
        
        api_collector = NewsCollector()
        api_count = api_collector.fetch_recent_news()
        
        from src.collectors.rss_collector import RSSCollector
        rss_collector = RSSCollector()
        rss_count = rss_collector.fetch_recent_news()
        
        twitter_collector = TwitterCollector()
        twitter_count = twitter_collector.fetch_top_updates()
        
        social_collector = SocialMediaCollector()
        trending_count = social_collector.fetch_trending_india()


        
        from src.collectors.gnews_collector import GNewsCollector
        gnews_collector = GNewsCollector()
        gnews_count = gnews_collector.fetch_country_news()
        
        total_count = api_count + rss_count + twitter_count + trending_count + gnews_count
        logger.info(f"Collected {total_count} new articles (incl. {gnews_count} GNews, {twitter_count} Twitter, {trending_count} Trending).")
        
        if total_count == 0 and db.query(RawNews).count() == 0:
            logger.warning("No news collected and DB is empty. Aborting cycle.")
            return

        # 2. Verify
        logger.info("Step 2: Verification")
        verifier = VerificationEngine()
        unprocessed = db.query(RawNews).filter(RawNews.processed == False).all()
        verified_count = verifier.verify_batch(db, [n.id for n in unprocessed])
        logger.info(f"Verified {verified_count} articles.")

        # 3. Analyze (Parallelized)
        logger.info("Step 3: Analysis (Parallel)")
        analyzer = LLMAnalyzer()
        unanalyzed = db.query(VerifiedNews).filter(VerifiedNews.impact_score == None).all()
        
        if unanalyzed:
            # Separate Sports from other news for specialized analysis
            sports_articles = []
            other_articles = []
            
            for n in unanalyzed:
                is_likely_sports = False
                if n.raw_news and n.raw_news.source_id:
                    sid = n.raw_news.source_id.lower()
                    if any(k in sid for k in ["sport", "espn", "football", "cricket"]):
                        is_likely_sports = True
                
                if not is_likely_sports and n.title:
                    title_lower = n.title.lower()
                    if any(k in title_lower for k in ["match", "tournament", "scored", "wicket", "stadium", "athlete", "cricket", "football", "olympic", "fifa", "premier league"]):
                        is_likely_sports = True
                
                article_data = {
                    "title": n.title, 
                    "content": n.content,
                    "source_name": n.raw_news.source_name if n.raw_news else "Source"
                }
                
                if is_likely_sports:
                    sports_articles.append((n, article_data))
                else:
                    other_articles.append((n, article_data))
            
            # Helper to map analysis result to VerifiedNews model
            def apply_analysis_to_news(news, result):
                news.summary_bullets = result.get("summary_bullets", [])
                news.why_it_matters = result.get("why_it_matters", "")
                news.who_is_affected = result.get("who_is_affected", "")
                news.short_term_impact = result.get("short_term_impact", "")
                news.long_term_impact = result.get("long_term_impact", "")
                news.sentiment = result.get("sentiment", "Neutral")
                news.impact_tags = result.get("impact_tags", [])
                news.bias_rating = result.get("bias_rating", "Neutral")
                news.impact_score = result.get("impact_score", 5)
                
                # Geography Handling
                news.country = result.get("country") or result.get("primary_geography") or (news.raw_news.country if news.raw_news else None)
                
                # Explicit Category Handling
                if news.raw_news and news.raw_news.source_id and news.raw_news.source_id.startswith("x-"):
                    cat = "Twitter 𝕏"
                else:
                    cat = result.get("category", "General")
                    if news.raw_news and news.raw_news.source_id:
                        sid = news.raw_news.source_id.lower()
                        mapping = {
                            "sport": "Sports", "espn": "Sports", "tech": "Technology", "wired": "Technology",
                            "politics": "Politics", "politico": "Politics", "business": "Business & Economy",
                            "cnbc": "Business & Economy", "wsj": "Business & Economy", "world": "World News",
                            "aljazeera": "World News", "india": "India / Local News", "ndtv": "India / Local News",
                            "science": "Science & Health", "nasa": "Science & Health", "mit": "AI & Machine Learning",
                            "ai": "AI & Machine Learning"
                        }
                        for key, val in mapping.items():
                            if key in sid:
                                cat = val
                                break
                news.category = cat

            # Run specialized Sports analysis
            if sports_articles:
                logger.info(f"Analyzing {len(sports_articles)} articles with Sports AI Editor...")
                sports_results = await analyzer.analyze_batch([a[1] for a in sports_articles], is_sports=True)
                for (news, _), result in zip(sports_articles, sports_results):
                    apply_analysis_to_news(news, result)
                    news.category = "Sports" # Force Sports
            
            # Run standard analysis for others
            if other_articles:
                logger.info(f"Analyzing {len(other_articles)} articles with Standard AI...")
                other_results = await analyzer.analyze_batch([a[1] for a in other_articles], is_sports=False)
                for (news, _), result in zip(other_articles, other_results):
                    apply_analysis_to_news(news, result)
            
            db.commit()
            logger.info(f"Analyzed {len(unanalyzed)} articles in parallel (incl. {len(sports_articles)} sports).")

        # 4. Generate Digest
        logger.info("Step 4: Digest Generation")
        generator = DigestGenerator()
        digest = await generator.create_daily_digest(db)

        # 5. Deliver
        if digest:
            if "brief" in digest:
                NotificationManager.send_daily_brief(db, digest["brief"])
            if "top_stories" in digest:
                for story in digest["top_stories"][:2]:
                    NotificationManager.notify_subscribers(db, story.get("category", "General"), story["title"], story["url"])

    except Exception as e:
        logger.error(f"Error in news cycle: {e}", exc_info=True)
    finally:
        db.close()
        logger.info("News Cycle Completed.")


async def run_twitter_only_cycle():
    """Lightweight cycle just for Twitter and Dashboard updates."""
    logger.info("Starting Lightweight Twitter Cycle...")
    db = SessionLocal()
    try:
        # 1. Collect Twitter
        twitter_collector = TwitterCollector()
        twitter_count = twitter_collector.fetch_top_updates()
        logger.info(f"Collected {twitter_count} tweets.")

        # 2. Force Digest Generation (This also promotes raw tweets to verified in our patched generator)
        generator = DigestGenerator()
        await generator.create_daily_digest(db)
        logger.info("Digest updated with fresh Twitter intelligence.")

    except Exception as e:
        logger.error(f"Error in twitter cycle: {e}")
    finally:
        db.close()
        logger.info("Twitter Cycle Completed.")

def start_scheduler():
    scheduler = BackgroundScheduler()
    
    # Run every 15 minutes (Balanced Update Cycle)
    from datetime import datetime, timedelta
    # Increase delay to 10 seconds to allow web server to fully stabilize and pass health checks on HF
    run_date = datetime.now() + timedelta(seconds=10)
    
    # helper to run async in background
    def _run_async_cycle():
        import asyncio
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(run_news_cycle())
        loop.close()

    def _run_async_twitter():
        import asyncio
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(run_twitter_only_cycle())
        loop.close()

    # Full News Cycle (Run immediately on boot + every 15 minutes)
    scheduler.add_job(_run_async_cycle, 'interval', minutes=15, next_run_time=run_date, id='full_news_cycle')
    
    # Daily Newspaper Update
    scheduler.add_job(
        _run_async_cycle, 
        'cron', 
        hour=6, 
        minute=30, 
        timezone='Asia/Kolkata',
        id='daily_newspaper_update'
    )
    
    scheduler.start()
    return scheduler
