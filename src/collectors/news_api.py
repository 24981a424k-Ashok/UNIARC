from datetime import datetime, timedelta
import logging
from typing import List, Dict, Any
from newsapi import NewsApiClient
from src.config.settings import NEWS_API_KEY
from src.database.models import SessionLocal, RawNews

logger = logging.getLogger(__name__)

class NewsCollector:
    def __init__(self):
        self.api_key = NEWS_API_KEY
        if not self.api_key:
            logger.warning("NewsAPI Key is missing!")
            self.client = None
        else:
            self.client = NewsApiClient(api_key=self.api_key)

    def fetch_recent_news(self, query: str = None, domains: str = None, categories: str = None) -> int:
        """
        Fetch news from the last 24 hours and save to DB.
        Returns count of new articles saved.
        """
        if not self.client:
            logger.error("NewsAPI client not initialized.")
            return 0

        # Time range: last 24 hours
        to_date = datetime.utcnow()
        from_date = to_date - timedelta(hours=24)
        
        try:
            # We can customize this to fetch top headlines or everything
            # For this agent, we might want 'everything' for breadth or 'top-headlines' for quality
            # Let's start with top headlines for major categories
            
            # Fetch all top headlines in one call to save quota (100 articles)
            response = self.client.get_top_headlines(
                language='en',
                page_size=70  # General headlines
            )
            
            # Dedicated Business Fetch
            business_response = self.client.get_top_headlines(
                language='en',
                category='business',
                country='in',
                page_size=30
            )

            # Dedicated Sports Fetch
            sports_response = self.client.get_top_headlines(
                language='en',
                category='sports',
                page_size=30
            )

            # 4. Search for recent sports and business news specifically to broaden density
            # DISABLED for FREE TIER: get_everything is restricted
            search_response = {'status': 'ok', 'articles': []}
            # search_response = self.client.get_everything(
            #     q='sports OR "IPL" OR "Cricket" OR "Football"',
            #     language='en',
            #     sort_by='publishedAt',
            #     page_size=40
            # )

            biz_search = {'status': 'ok', 'articles': []}
            # biz_search = self.client.get_everything(
            #     q='business OR economy OR startup OR "Stock Market"',
            #     language='en',
            #     sort_by='publishedAt',
            #     page_size=40
            # )

            all_articles = []
            if response['status'] == 'ok':
                all_articles.extend(response.get('articles', []))
            
            if business_response['status'] == 'ok':
                all_articles.extend(business_response.get('articles', []))
            
            if sports_response['status'] == 'ok':
                all_articles.extend(sports_response.get('articles', []))

            if search_response['status'] == 'ok':
                all_articles.extend(search_response.get('articles', []))

            if biz_search['status'] == 'ok':
                all_articles.extend(biz_search.get('articles', []))
            
            # 5. Dedicated Country Fetch (Japan, USA)
            target_countries = ['jp', 'us']
            for country_code in target_countries:
                try:
                    country_res = self.client.get_top_headlines(
                        language='en' if country_code != 'jp' and country_code != 'cn' else None,
                        country=country_code,
                        page_size=20
                    )
                    if country_res['status'] == 'ok':
                        # Tag these articles with the country code before saving
                        articles = country_res.get('articles', [])
                        for a in articles:
                            a['target_country'] = country_code
                        all_articles.extend(articles)
                except Exception as ce:
                    logger.warning(f"Failed to fetch news for {country_code}: {ce}")

            stats = self._save_articles(all_articles)
            return stats
            
        except Exception as e:
            logger.error(f"Error fetching news: {e}")
            return {"new": 0, "duplicates": 0, "total": 0}

    def _save_articles(self, articles: List[Dict[str, Any]]) -> Dict[str, int]:
        count = 0
        dupe_count = 0
        seen_urls = set()
        
        for article in articles:
            session = SessionLocal()
            try:
                url = article.get('url')
                if not url or url in seen_urls:
                    continue
                
                # Check for duplicates
                exists = session.query(RawNews).filter(RawNews.url == url).first()
                if exists:
                    dupe_count += 1
                    seen_urls.add(url)
                    continue
                
                # ... same saving logic
                # (Skipping middle code for brevity in tool call, 
                # but making sure the replacement is robust)
                
                # Parse date
                pub_date = article.get('publishedAt')
                pub_dt = datetime.utcnow()
                if pub_date:
                    try:
                        pub_dt = datetime.strptime(pub_date, "%Y-%m-%dT%H:%M:%SZ")
                    except ValueError: pass

                raw_news = RawNews(
                    source_id=article.get('source', {}).get('id'),
                    source_name=article.get('source', {}).get('name'),
                    author=article.get('author'),
                    title=article.get('title'),
                    description=article.get('description'),
                    url=url,
                    url_to_image=article.get('urlToImage'),
                    published_at=pub_dt,
                    content=article.get('content'),
                    country=article.get('target_country')
                )
                session.add(raw_news)
                session.commit()
                seen_urls.add(url)
                count += 1
            except Exception as e:
                session.rollback()
                if "UniqueViolation" not in str(e) and "Duplicate" not in str(e):
                    logger.warning(f"Error saving article {article.get('title')}: {e}")
            finally:
                session.close()
        
        stats = {"new": count, "duplicates": dupe_count, "total": len(articles)}
        if count > 0:
            logger.info(f"Successfully saved {count} new articles to intelligence node (Duplicates skipped: {dupe_count}).")
        return stats

if __name__ == "__main__":
    # Test run
    collector = NewsCollector()
    collector.fetch_recent_news()
