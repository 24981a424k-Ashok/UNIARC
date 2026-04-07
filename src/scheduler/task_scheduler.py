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
from src.config.firebase_config import initialize_firebase

from loguru import logger

async def run_news_cycle():
    logger.info("Starting Daily News Cycle...")
    initialize_firebase()
    db = SessionLocal()
    
    try:
        # 1. Collect
        logger.info("Step 1: Collection")
        
        # 1. Individual Collector Stats (Pre-initialized for Zero Error)
        api_res = {"new": 0, "duplicates": 0, "total": 0}
        rss_res = {"new": 0, "duplicates": 0, "total": 0}
        twitter_res = {"new": 0, "duplicates": 0, "total": 0}
        trending_res = {"new": 0, "duplicates": 0, "total": 0}
        gnews_res = {"new": 0, "duplicates": 0, "total": 0}
        newsdata_res = {"new": 0, "duplicates": 0, "total": 0}

        api_collector = NewsCollector()
        api_res = api_collector.fetch_recent_news() 
        
        from src.collectors.rss_collector import RSSCollector
        rss_collector = RSSCollector()
        rss_res = rss_collector.fetch_recent_news() 
        
        twitter_collector = TwitterCollector()
        twitter_res = twitter_collector.fetch_top_updates()
        
        social_collector = SocialMediaCollector()
        trending_res = social_collector.fetch_trending_india()

        from src.collectors.gnews_collector import GNewsCollector
        gnews_collector = GNewsCollector()
        gnews_res = gnews_collector.fetch_country_news() 

        from src.collectors.newsdata_collector import NewsDataCollector
        newsdata_collector = NewsDataCollector()
        newsdata_res = newsdata_collector.fetch_student_focus_news() 
        
        # 2. Aggregation Logic with Type Safety
        def get_stat(res, key):
            if isinstance(res, dict): return res.get(key, 0)
            return res if key == "new" else 0

        new_count = (
            get_stat(api_res, "new") + get_stat(rss_res, "new") + 
            get_stat(twitter_res, "new") + get_stat(trending_res, "new") + 
            get_stat(gnews_res, "new") + get_stat(newsdata_res, "new")
        )
        dupe_count = (
            get_stat(api_res, "duplicates") + get_stat(rss_res, "duplicates") + 
            get_stat(twitter_res, "duplicates") + get_stat(trending_res, "duplicates") + 
            get_stat(gnews_res, "duplicates") + get_stat(newsdata_res, "duplicates")
        )
        total_api_checked = (
            get_stat(api_res, "total") + get_stat(rss_res, "total") + 
            get_stat(twitter_res, "total") + get_stat(trending_res, "total") + 
            get_stat(gnews_res, "total") + get_stat(newsdata_res, "total")
        )

        logger.info(f"News Cycle: Checked {total_api_checked} sources, found {dupe_count} duplicates.")
        logger.info(f"Intelligence Update: Saved {new_count} new articles.")
        
        if new_count == 0 and db.query(RawNews).count() == 0:
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

            # Run specialized Sports analysis (Isolated waves)
            if sports_articles:
                logger.info(f"Analyzing {len(sports_articles)} articles with Sports AI...")
                wave_size = 5
                for i in range(0, len(sports_articles), wave_size):
                    try:
                        wave = sports_articles[i:i + wave_size]
                        sports_results = await analyzer.analyze_batch([a[1] for a in wave], is_sports=True)
                        for (news, _), result in zip(wave, sports_results):
                            apply_analysis_to_news(news, result)
                            news.category = "Sports"
                        db.commit() # Save this wave immediately!
                        logger.info(f"Progress: Processed {min(i + wave_size, len(sports_articles))}/{len(sports_articles)} sports articles.")
                    except Exception as e:
                        logger.error(f"Sports analysis wave failed: {e}")
                        continue # Keep the cycle moving!
            
            # Run standard analysis (Isolated waves)
            if other_articles:
                logger.info(f"Analyzing {len(other_articles)} articles with Standard AI...")
                wave_size = 10 
                for i in range(0, len(other_articles), wave_size):
                    try:
                        wave = other_articles[i:i + wave_size]
                        other_results = await analyzer.analyze_batch([a[1] for a in wave], is_sports=False)
                        for (news, _), result in zip(wave, other_results):
                            apply_analysis_to_news(news, result)
                        db.commit() # Save this wave immediately!
                        logger.info(f"Progress: Processed {min(i + wave_size, len(other_articles))}/{len(other_articles)} standard articles.")
                    except Exception as e:
                        logger.error(f"Standard analysis wave failed: {e}")
                        continue # Keep the cycle moving!

            logger.info(f"Analyzed {len(unanalyzed)} articles incrementally.")

        # --- MANDATORY PHASE: Ensure the website updates even if AI failed ---
        try:
            # 4. Generate Digest (The core source of the "Entire Website")
            logger.info("Step 4: Mandatory Website Update (Digest Generation)...")
            generator = DigestGenerator()
            digest = await generator.create_daily_digest(db)

            # 5. Deliver
            if digest:
                if "brief" in digest:
                    NotificationManager.send_daily_brief(db, digest["brief"])
                if "top_stories" in digest:
                    for story in digest["top_stories"][:2]:
                        NotificationManager.notify_subscribers(db, story.get("category", "General"), story["title"], story["url"], story.get("id"))
                
                # 6. Check Topic Tracking
                logger.info("Step 6: Topic Tracking Notifications")
                await check_topic_tracking(db)
        except Exception as e:
            logger.error(f"Website update (Digest/Delivery) failed: {e}")

    except Exception as e:
        logger.error(f"Fatal error in news cycle: {e}")
        # Re-read if it was just a transient DB error
        if "psycopg2" in str(e).lower() or "connection" in str(e).lower():
            import asyncio
            await asyncio.sleep(2)
    finally:
        db.close()
        logger.info("--------------------------------------------------")
        logger.info("✅ NEWS CYCLE: EXECUTION COMPLETED SUCCESSFULLY ✅")
        logger.info("--------------------------------------------------")
        logger.info("News Cycle Completed.")

async def check_topic_tracking(db: Session):
    """Check for new articles matching tracked topics and notify users."""
    try:
        from src.database.models import TopicTracking, VerifiedNews, User, TrackNotification
        from src.delivery.notifications import NotificationManager
        from datetime import datetime, timedelta
        
        # Look for tracks created or updated recently
        # In a real system, we'd track 'last_notified_at'
        # For now, look for news from the last hour that matches active tracks
        one_hour_ago = datetime.utcnow() - timedelta(hours=1)
        new_articles = db.query(VerifiedNews).filter(VerifiedNews.created_at > one_hour_ago).all()
        
        if not new_articles:
            return

        tracks = db.query(TopicTracking).filter(TopicTracking.notify_sms == True).all()
        
        for track in tracks:
            user = track.user
            if not user or not user.phone:
                continue
            
            for article in new_articles:
                # Basic keyword matching
                match = False
                for kw in (track.topic_keywords or []):
                    if kw.lower() in article.title.lower() or kw.lower() in (article.category or "").lower():
                        match = True
                        break
                
                if match:
                    # CHECK FOR DUPLICATE
                    already_notified = db.query(TrackNotification).filter(
                        TrackNotification.user_id == user.id,
                        TrackNotification.news_id == article.id
                    ).first()
                    
                    if not already_notified:
                        logger.info(f"Topic Match Found! Notifying {user.phone} for '{article.title}'")
                        NotificationManager.send_sms(
                            user.phone, 
                            f"Tracked Intelligence: '{article.title}' matches your search. Read more: {article.url}"
                        )
                        # RECORD NOTIFICATION
                        db.add(TrackNotification(user_id=user.id, news_id=article.id))
                        db.commit()
                    
    except Exception as e:
        logger.error(f"Error in topic tracking check: {e}")


async def run_twitter_only_cycle():
    """Lightweight cycle just for Twitter and Dashboard updates."""
    logger.info("Starting Lightweight Twitter Cycle...")
    initialize_firebase()
    db = SessionLocal()
    try:
        # 1. Collect Twitter
        twitter_collector = TwitterCollector()
        twitter_res = twitter_collector.fetch_top_updates()
        logger.info(f"Collected {twitter_res.get('new', 0)} tweets.")

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
    # Configure scheduler with higher concurrency to prevent "skipped" cycles
    job_defaults = {
        'coalesce': False,
        'max_instances': 3,
        'misfire_grace_time': 3600
    }
    scheduler = BackgroundScheduler(job_defaults=job_defaults)
    
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

    # 4. Immediate Startup Trigger (Safety First)
    # Check if we have fresh news. If not, trigger a cycle 5s after boot.
    run_date = datetime.now() + timedelta(seconds=5)
    scheduler.add_job(_run_async_cycle, 'interval', minutes=15, next_run_time=run_date, id='full_news_cycle', replace_existing=True)
    logger.info("News Cycle Scheduled: Every 15m. Startup trigger in 5s.")
    
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
