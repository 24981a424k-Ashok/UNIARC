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

            saved_count = self._save_articles(all_articles)
            return saved_count
            
        except Exception as e:
            logger.error(f"Error fetching news: {e}")
            return 0

    def _save_articles(self, articles: List[Dict[str, Any]]) -> int:
        session = SessionLocal()
        count = 0
        seen_urls = set()
        try:
            for article in articles:
                url = article.get('url')
                if not url:
                    continue
                
                # Check for duplicates
                # Check for duplicates (DB + Current Batch)
                if url in seen_urls:
                    continue
                
                exists = session.query(RawNews).filter(RawNews.url == url).first()
                if exists:
                    continue
                
                seen_urls.add(url)
                
                # Parse date
                pub_date = article.get('publishedAt')
                if pub_date:
                    try:
                        # NewsAPI format: 2024-01-23T12:00:00Z
                        pub_dt = datetime.strptime(pub_date, "%Y-%m-%dT%H:%M:%SZ")
                    except ValueError:
                        pub_dt = datetime.utcnow()
                else:
                    pub_dt = datetime.utcnow()

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
                count += 1
            
            session.commit()
            logger.info(f"Saved {count} new articles.")
            return count
        except Exception as e:
            logger.error(f"Database error: {e}")
            session.rollback()
            return 0
        finally:
            session.close()

if __name__ == "__main__":
    # Test run
    collector = NewsCollector()
    collector.fetch_recent_news()
