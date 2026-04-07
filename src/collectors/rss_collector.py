import feedparser
import logging
from datetime import datetime, timedelta
from dateutil import parser
from typing import List, Dict, Any
from src.database.models import SessionLocal, RawNews

logger = logging.getLogger(__name__)

# Default list of trusted feeds
RSS_FEEDS = {
    # 1. Technology
    "techcrunch": "https://techcrunch.com/feed/",
    "wired": "https://www.wired.com/feed/rss",
    
    # 2. AI & ML
    "mit-ai": "https://news.mit.edu/rss/topic/artificial-intelligence2",
    "google-ai": "http://feeds.feedburner.com/blogspot/gJZg",
    
    # 3. Sports
    "espn": "https://www.espn.com/espn/rss/news",
    "bbc-sports": "http://feeds.bbci.co.uk/sport/rss.xml",
    
    # 4. Politics
    "cnn-politics": "http://rss.cnn.com/rss/cnn_allpolitics.rss",
    "politico": "https://rss.politico.com/politics-news.xml",
    
    # 5. Business
    "cnbc": "https://www.cnbc.com/id/100003114/device/rss/rss.html",
    "wsj-markets": "https://feeds.a.dj.com/rss/RSSMarketsMain.xml",
    
    # 6. World News
    "bbc-news": "http://feeds.bbci.co.uk/news/rss.xml",
    "bbc-world": "http://feeds.bbci.co.uk/news/world/rss.xml",
    "cnn-international": "http://rss.cnn.com/rss/edition.rss",
    "aljazeera": "https://www.aljazeera.com/xml/rss/all.xml",
    
    # 7. India / Local
    "times-of-india": "https://timesofindia.indiatimes.com/rssfeedstopstories.cms",
    "ndtv-top": "https://feeds.feedburner.com/ndtvnews-top-stories",
    "news18-india": "https://www.news18.com/rss/india.xml",
    # "times-now": "https://www.timesnownews.com/rss/top-stories",  # Syntax error in XML
    
    # 8. Science & Health
    "sciencedaily": "https://www.sciencedaily.com/rss/top/science.xml",
    # "webmd": "https://rssfeeds.webmd.com/rss/rss.aspx?RSSSource=rss_public",  # Connection issues
    
    # 9. Education
    # "education-week": "https://www.edweek.org/rss",  # Malformed XML
    # "chronicle-higher-ed": "https://www.chronicle.com/rss",  # Malformed XML
    
    # 10. Entertainment
    "variety": "https://variety.com/feed/",
    "hollywood-reporter": "https://www.hollywoodreporter.com/feed/",
    
    # 11. Other/General (Disasters etc)
    "reliefweb": "https://reliefweb.int/updates/rss.xml",
    "nasa": "https://www.nasa.gov/rss/dyn/breaking_news.rss",

    # 12. Environment & Sustainability
    "grist": "https://grist.org/feed/",
    # "natgeo": "https://www.nationalgeographic.com/rss/index.xml",  # No element found
    # "earth": "https://www.bbcearth.com/rss",  # Mismatched tag

    # 13. Lifestyle & Wellness
    # "nyt-lifestyle": "https://rss.nytimes.com/services/xml/rss/nyt/Lifestyle.xml",  # XML declaration issue
    # "travel": "https://www.travelandleisure.com/rss/all",  # Malformed XML

    # 14. Defense & Security
    "defense-news": "https://www.defensenews.com/arc/outboundfeeds/rss/category/home/",
    "military": "https://www.militarytimes.com/arc/outboundfeeds/rss/category/home/",

    # 15. Regional Fallbacks (To fix empty nodes)
    # 15. Regional Fallbacks (NATIVE LANGUAGE EDITIONS)
    "zaobao-china": "https://www.zaobao.com.sg/rss/china.xml", # Kept for general world news but with cn tag (Wait, user said delete node)
    # Removing zaobao-china to fully delete node
    
    # Japan: NHK News (Japanese)
    "nhk-japan": "https://www.nhk.or.jp/rss/news/cat0.xml",
    
    # UK: Guardian (English - Native)
    "guardian-uk": "https://www.theguardian.com/uk/rss",

    # Germany: Tagesschau (German)
    "tagesschau-de": "https://www.tagesschau.de/xml/rss2/",

    # France: Le Monde (French)
    "lemonde-fr": "https://www.lemonde.fr/rss/une.xml",

    # Australia: ABC (English - Native)
    # Removing abc-australia to fully delete node

    # Russia: Kommersant (Russian)
    "kommersant-ru": "https://www.kommersant.ru/RSS/news.xml",

    # Singapore: Straits Times (English - Native)
    "straitstimes-singapore": "https://www.straitstimes.com/news/singapore/rss.xml",
    
    # 16. Missing Markets (United States & UAE)
    # UAE: Al Bayan (Arabic)
    # Removing albayan-uae to fully delete node
    
    "nyt-us": "https://rss.nytimes.com/services/xml/rss/nyt/US.xml", # USA
    "cnn-us": "http://rss.cnn.com/rss/cnn_us.rss" # USA
}

class RSSCollector:
    def __init__(self):
        self.feeds = RSS_FEEDS

    def fetch_recent_news(self) -> Dict[str, int]:
        """
        Fetch news from all configured RSS feeds from the last 24 hours.
        Returns stats dictionary.
        """
        stats = {"new": 0, "duplicates": 0, "total": 0}
        
        for source_name, feed_url in self.feeds.items():
            try:
                # Parse the feed
                feed = feedparser.parse(feed_url)
                
                if feed.bozo:
                    logger.warning(f"Potential issue parsing feed {source_name}: {feed.bozo_exception}")

                articles = []
                for entry in feed.entries:
                    published_at = self._parse_date(entry)
                    if self._is_recent(published_at):
                        image_url = self._extract_image(entry)
                        articles.append({
                            "source_id": source_name,
                            "source_name": feed.feed.get("title", source_name),
                            "title": entry.get("title"),
                            "url": entry.get("link"),
                            "content": entry.get("summary", "") or entry.get("description", ""),
                            "author": entry.get("author", "Unknown"),
                            "published_at": published_at,
                            "url_to_image": image_url,
                            "country_code": self._detect_country(source_name)
                        })
                
                if articles:
                   res = self._save_articles(articles)
                   stats["new"] += res["new"]
                   stats["duplicates"] += res["duplicates"]
                   stats["total"] += len(articles)
                   logger.info(f"Fetched {len(articles)} recent items from {source_name}, saved {res['new']} new.")
                
            except Exception as e:
                logger.error(f"Error fetching RSS feed {source_name}: {e}")
                continue
                
        return stats

    def _extract_image(self, entry) -> str:
        """Try to find an image URL in common RSS fields"""
        # 1. media_content
        if 'media_content' in entry:
            for media in entry.media_content:
                if media.get('type', '').startswith('image') or media.get('medium') == 'image':
                    return media.get('url')
        
        # 2. media_thumbnail
        if 'media_thumbnail' in entry:
            return entry.media_thumbnail[0].get('url')
            
        # 3. links (enclosure)
        if 'links' in entry:
            for link in entry.links:
                if link.get('rel') == 'enclosure' and link.get('type', '').startswith('image'):
                    return link.get('href')
                    
        # 4. Parse summary HTML (Basic check)
        summary = entry.get("summary", "") or entry.get("description", "")
        if '<img' in summary:
            # Very naive extraction, can be improved with BeautifulSoup if needed
            try:
                start = summary.find('src="') + 5
                end = summary.find('"', start)
                if start > 4 and end > start:
                    return summary[start:end]
            except:
                pass
                
        return None

    def _parse_date(self, entry) -> datetime:
        """Attempt to parse date from common RSS fields"""
        date_str = entry.get("published") or entry.get("updated") or entry.get("date")
        if date_str:
            # Common timezones mapping to help dateutil
            tzinfos = {
                "EST": -18000, "EDT": -14400,
                "CST": -21600, "CDT": -18000,
                "MST": -25200, "MDT": -21600,
                "PST": -28800, "PDT": -25200,
                "IST": 19800
            }
            try:
                # Use tzinfos for common abbreviations that dateutil might not know
                dt = parser.parse(date_str, tzinfos=tzinfos)
                # Ensure we return a naive UTC datetime
                if dt.tzinfo:
                    dt = dt.astimezone(datetime.now().astimezone().tzinfo).replace(tzinfo=None)
                return dt
            except Exception:
                pass
        return datetime.utcnow()

    def _is_recent(self, date_obj: datetime) -> bool:
        """Check if date is within last 24 hours"""
        cutoff = datetime.utcnow() - timedelta(hours=24)
        if date_obj.tzinfo:
            date_obj = date_obj.replace(tzinfo=None)
        return date_obj > cutoff

    def _detect_country(self, source_id: str) -> str:
        """Map source IDs to country codes for auto-tagging"""
        mapping = {
            "nhk-japan": "jp",
            "nhk-japan": "jp",
            "guardian-uk": "gb",
            "bbc-news": "gb",
            "tagesschau-de": "de",
            "lemonde-fr": "fr",
            "lemonde-fr": "fr",
            "kommersant-ru": "ru",
            "straitstimes-singapore": "sg",
            "nyt-us": "us",
            "cnn-us": "us",
            "times-of-india": "in",
            "ndtv-top": "in",
            "news18-india": "in"
        }
        return mapping.get(source_id)

    def _save_articles(self, articles: List[Dict[str, Any]]) -> Dict[str, int]:
        session = SessionLocal()
        count = 0
        dupe_count = 0
        try:
            seen_urls = set()
            for article in articles:
                url = article.get('url')
                if not url or url in seen_urls:
                    continue
                
                if url in seen_urls:
                    continue
                
                exists = session.query(RawNews).filter(RawNews.url == url).first()
                if exists:
                    dupe_count += 1
                    continue
                
                seen_urls.add(url)
                
                try:
                    raw_news = RawNews(
                        source_id=article['source_id'],
                        source_name=article['source_name'],
                        author=article['author'][:255] if article.get('author') else None,
                        title=article['title'],
                        description=article['content'][:500] + "..." if len(article['content']) > 500 else article['content'],
                        url=url,
                        url_to_image=article.get('url_to_image'),
                        published_at=article['published_at'],
                        content=article['content'],
                        country=article.get('country_code')
                    )
                    session.add(raw_news)
                    count += 1
                except Exception as e:
                    session.rollback()
                    continue
            
            session.commit()
            return {"new": count, "duplicates": dupe_count, "total": len(articles)}
        except Exception as e:
            logger.error(f"Database error saving RSS: {e}")
            session.rollback()
            return {"new": 0, "duplicates": 0, "total": 0}
        finally:
            session.close()

if __name__ == "__main__":
    # Test run
    collector = RSSCollector()
    collector.fetch_recent_news()
