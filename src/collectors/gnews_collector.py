import os
import requests
import logging
from datetime import datetime
from typing import List, Dict, Any
from src.database.models import SessionLocal, RawNews
from dotenv import load_dotenv

from src.config import settings

load_dotenv()
logger = logging.getLogger(__name__)

class GNewsCollector:
    def __init__(self):
        self.api_keys = []
        if settings.GNEWS_API_KEY:
            self.api_keys.append(settings.GNEWS_API_KEY)
        if settings.GNEWS_API_KEY_2:
            self.api_keys.append(settings.GNEWS_API_KEY_2)
            
        self.base_url = "https://gnews.io/api/v4"
        if not self.api_keys:
            logger.warning("GNews API Key is missing!")
            
    def _get_api_key(self):
        """Rotate keys to distribute load"""
        import random
        if not self.api_keys: return None
        return random.choice(self.api_keys)

    def fetch_country_news(self, countries: List[str] = ['us', 'gb', 'jp', 'in', 'ru', 'de', 'fr', 'sg']) -> int:
        """
        Fetch specialized intelligence and top headlines for specific countries.
        """
        if not self.api_keys:
            return 0

        total_saved = 0
        
        # Specialized Country Features Mapping
        specialized_features = {
            'us': '("Stock Market" OR "Fed News" OR "Corporate News" OR "AI" OR "Tech" OR "Startup")',
            'gb': '("Policy" OR "Regulation" OR "Global Finance" OR "UK–EU relations")',
            'de': '("EU economy" OR "Industry news" OR "Energy policy" OR "Climate policy")',
            'jp': '("Technology" OR "Robotics" OR "Market" OR "Currency")',
            'sg': '("Startup" OR "Fintech" OR "ASEAN economy")',
            'in': '("Policy" OR "Market" OR "Economy" OR "Tech" OR "Startup" OR "Infrastructure")'
        }

        # OPTIMIZATION: Rotate countries to avoid Rate Limits (now 200 req/day with 2 keys)
        # 15 min cycle = 96 runs/day. 
        # With 2 keys, we can afford ~2 req/run * 2 keys = 4 requests per run?
        # Let's increase target countries to 3 to be safe and cover more ground.
        target_countries = []
        priority_countries = ['in', 'us']
        
        # 1. Add priority countries first
        for pc in priority_countries:
            if pc in countries:
                target_countries.append(pc)
        
        # 2. Fill remaining slots with random countries
        remaining = [c for c in countries if c not in target_countries]
        import random
        random.shuffle(remaining)
        
        # Max 4 countries per run (assuming 2 keys * 100 req/day / 96 runs = ~2 req/run. 
        # But we rotate keys, so effectively we can do a bit more if we have multiple keys)
        # If we have 2 keys, we can handle ~4 requests per 15 min cycle safely.
        slots_left = 4 - len(target_countries)
        if slots_left > 0:
            target_countries.extend(remaining[:slots_left])
            
        logger.info(f"GNews: Cycle Targets: {target_countries}")

        for country in target_countries:
            try:
                queries = [None] # Default to top headlines
                if country in specialized_features:
                    queries.append(specialized_features[country])

                for query in queries:
                    endpoint = "search" if query else "top-headlines"
                    current_key = self._get_api_key()
                    logger.info(f"GNews: Fetching {endpoint} for {country} (Query: {query})...")
                    
                    params = {
                        "lang": "en" if country not in ['jp', 'cn', 'ru', 'de', 'fr'] else None,
                        "country": country,
                        "max": 10,
                        "apikey": current_key
                    }
                    
                    if query: params["q"] = query
                    
                    # For non-English countries, GNews often works better with localized lang or no lang constraint
                    if not query: # Only override lang for general top-headlines
                        if country == 'jp': params['lang'] = 'ja'
                        if country == 'ru': params['lang'] = 'ru'
                        if country == 'de': params['lang'] = 'de'
                        if country == 'fr': params['lang'] = 'fr'
                        if country == 'in': params['lang'] = 'en' # India often wants English, but can support 'hi' if requested
                    
                    response = requests.get(f"{self.base_url}/{endpoint}", params=params)
                    if response.status_code == 200:
                        articles = response.json().get('articles', [])
                        total_saved += self._save_articles(articles, country)
                    else:
                        logger.error(f"GNews error for {country} ({endpoint}): {response.status_code} - {response.text}")
            except Exception as e:
                logger.error(f"GNews fetch failed for {country}: {e}")
        
        return total_saved

    def _save_articles(self, articles: List[Dict[str, Any]], country_code: str) -> int:
        session = SessionLocal()
        count = 0
        try:
            for article in articles:
                url = article.get('url')
                if not url:
                    continue
                
                # Check for duplicates
                exists = session.query(RawNews).filter(RawNews.url == url).first()
                if exists:
                    continue
                
                # GNews date format: 2024-02-13T12:00:00Z
                pub_date = article.get('publishedAt')
                try:
                    pub_dt = datetime.strptime(pub_date, "%Y-%m-%dT%H:%M:%SZ")
                except:
                    pub_dt = datetime.utcnow()

                raw_news = RawNews(
                    source_name=article.get('source', {}).get('name', 'GNews'),
                    author=None,
                    title=article.get('title'),
                    description=article.get('description'),
                    url=url,
                    url_to_image=article.get('image'),
                    published_at=pub_dt,
                    content=article.get('content'),
                    country=country_code
                )
                session.add(raw_news)
                count += 1
            
            session.commit()
            logger.info(f"GNews: Saved {count} articles for {country_code}.")
            return count
        except Exception as e:
            logger.error(f"GNews database error: {e}")
            session.rollback()
            return 0
        finally:
            session.close()

if __name__ == "__main__":
    collector = GNewsCollector()
    collector.fetch_country_news()
