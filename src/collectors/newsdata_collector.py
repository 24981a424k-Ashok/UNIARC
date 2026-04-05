import os
import logging
import requests
from datetime import datetime, timedelta
from typing import List, Dict, Any
from src.database.models import SessionLocal, RawNews
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

class NewsDataCollector:
    """
    Premium News Collector using NewsData.io API.
    Provides higher accuracy and deeper local news coverage for India.
    """
    
    def __init__(self):
        self.api_key = os.getenv("NEWSDATA_API_KEY")
        self.base_url = "https://newsdata.io/api/1/news"
        if not self.api_key:
            logger.warning("NewsData.io API Key is missing!")

    def fetch_student_focus_news(self, limit: int = 50) -> int:
        """
        Fetch news specifically for students (Education, Career, Exams in India).
        """
        if not self.api_key:
            return 0

        # Categories: education, science, technology
        # Keywords: exams, results, admission, scholarship, career, vacancy
        params = {
            "apikey": self.api_key,
            "q": "exams OR results OR admission OR scholarship OR JEE OR NEET OR UPSC OR GATE OR recruitment",
            "country": "in",
            "category": "education",
            "language": "en"
        }
        
        try:
            response = requests.get(self.base_url, params=params, timeout=15)
            response.raise_for_status()
            data = response.json()
            
            if data.get("status") != "success":
                logger.error(f"NewsData.io API error: {data.get('message')}")
                return {"new": 0, "duplicates": 0, "total": 0}
                
            results = data.get("results", [])
            logger.info(f"Fetched {len(results)} student-related articles from NewsData.io")
            
            stats = self._save_articles(results)
            return stats
        except Exception as e:
            logger.error(f"Error fetching from NewsData.io: {e}")
            return {"new": 0, "duplicates": 0, "total": 0}

    def _save_articles(self, articles: List[Dict[str, Any]]) -> Dict[str, int]:
        session = SessionLocal()
        count = 0
        dupe_count = 0
        seen_urls = set()
        try:
            for article in articles:
                url = article.get('link')
                if not url:
                    continue
                
                if url in seen_urls:
                    continue
                
                exists = session.query(RawNews).filter(RawNews.url == url).first()
                if exists:
                    dupe_count += 1
                    continue
                
                seen_urls.add(url)
                
                # Parse date (format: 2024-04-05 10:23:45)
                pub_date_str = article.get('pubDate')
                try:
                    pub_dt = datetime.strptime(pub_date_str, "%Y-%m-%d %H:%M:%S")
                except:
                    pub_dt = datetime.utcnow()

                raw_news = RawNews(
                    source_id=f"nd-{article.get('source_id')}",
                    source_name=article.get('source_id', 'NewsData.io'),
                    author=article.get('creator', [None])[0] if article.get('creator') else None,
                    title=article.get('title'),
                    description=article.get('description'),
                    url=url,
                    url_to_image=article.get('image_url'),
                    published_at=pub_dt,
                    content=article.get('content') or article.get('description'),
                    country='in'
                )
                session.add(raw_news)
                count += 1
            
            session.commit()
            stats = {"new": count, "duplicates": dupe_count, "total": len(articles)}
            logger.info(f"NewsData.io: Saved {count} new student articles (Duplicates skipped: {dupe_count}).")
            return stats
        except Exception as e:
            logger.error(f"Database error in NewsData: {e}")
            session.rollback()
            return {"new": 0, "duplicates": 0, "total": 0}
        finally:
            session.close()

if __name__ == "__main__":
    collector = NewsDataCollector()
    collector.fetch_student_focus_news()
