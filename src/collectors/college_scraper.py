import requests
from bs4 import BeautifulSoup
import logging
from datetime import datetime
from typing import List, Dict, Any
from src.database.models import SessionLocal, RawNews
import re
import asyncio

logger = logging.getLogger(__name__)

class CollegeScraper:
    def __init__(self):
        self.targets = [
            {
                "name": "IIT Delhi Placement",
                "url": "https://ocs.iitd.ac.in/",
                "country": "in",
                "category": "Education"
            },
            {
                "name": "Mumbai University Notices",
                "url": "https://mu.ac.in/notices",
                "country": "in",
                "category": "Education"
            }
        ]

    def run(self):
        """Run the scraper for all targets"""
        total_saved = 0
        for target in self.targets:
            try:
                logger.info(f"Scraping {target['name']}...")
                articles = self._scrape_site(target)
                if articles:
                    saved = self._save_articles(articles)
                    total_saved += saved
                    logger.info(f"Saved {saved} new notices from {target['name']}")
            except Exception as e:
                logger.error(f"Failed to scrape {target['name']}: {e}")
        return total_saved

    async def _scrape_site(self, name: str, url: str) -> List[Dict[str, Any]]:
        try:
            headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
            response = requests.get(url, headers=headers, timeout=15)
            response.raise_for_status() # Raise an exception for HTTP errors
            soup = BeautifulSoup(response.content, "html.parser")
            notices = []

            if "iitd.ac.in" in url:
                # IIT Delhi notices
                # The original IITD URL was ocs.iitd.ac.in, the new one is home.iitd.ac.in/news.php
                # Adjusting base URL for relative links accordingly.
                base_url = "https://home.iitd.ac.in"
                for link in soup.find_all("a", href=True):
                    text = link.text.strip()
                    if any(k in text.lower() for k in ["placement", "internship", "career", "job", "notice", "recruitment"]):
                        full_url = link["href"]
                        if not full_url.startswith("http"):
                            full_url = f"{base_url}{full_url}"
                        
                        # Ensure title is not empty
                        if text:
                            notices.append({
                                "title": text,
                                "url": full_url,
                                "content": f"Notice from {name}: {text}", # Added content field for consistency with RawNews
                                "source_name": name,
                                "source_id": name.lower().replace(" ", "_"), # Generate a source_id
                                "published_at": datetime.utcnow(), # Add published_at
                                "country": "in" # Assuming country for these universities
                            })
            elif "mu.ac.in" in url:
                # Mumbai University
                base_url = "https://mu.ac.in"
                for item in soup.find_all(["li", "a"]):
                    text = item.text.strip()
                    # Ensure text is long enough and contains relevant keywords
                    if len(text) > 10 and any(k in text.lower() for k in ["exam", "result", "admission", "notice", "circular"]):
                        href = item.get("href") if item.name == "a" else item.find("a").get("href") if item.find("a") else None
                        if href:
                            full_url = href
                            if not full_url.startswith("http"):
                                full_url = f"{base_url}{full_url}"
                            
                            notices.append({
                                "title": text,
                                "url": full_url,
                                "content": f"Notice from {name}: {text}",
                                "source_name": name,
                                "source_id": name.lower().replace(" ", "_"),
                                "published_at": datetime.utcnow(),
                                "country": "in"
                            })
            elif "annauniv.edu" in url:
                # Anna University
                base_url = "http://www.annauniv.edu"
                for link in soup.find_all("a", href=True):
                    text = link.text.strip()
                    if any(k in text.lower() for k in ["recruitment", "placement", "circular", "notification", "exam", "admission"]):
                        full_url = link["href"]
                        if not full_url.startswith("http"):
                            full_url = f"{base_url}/{full_url.lstrip('/')}" # Ensure correct path joining
                        
                        if text:
                            notices.append({
                                "title": text,
                                "url": full_url,
                                "content": f"Notice from {name}: {text}",
                                "source_name": name,
                                "source_id": name.lower().replace(" ", "_"),
                                "published_at": datetime.utcnow(),
                                "country": "in"
                            })
            elif "du.ac.in" in url:
                # Delhi University
                base_url = "https://www.du.ac.in"
                for item in soup.select(".news-ticker-item a, .content a"): # Broaden selection for DU
                    text = item.text.strip()
                    if any(k in text.lower() for k in ["placement", "hostel", "admission", "recruitment", "exam", "notice", "circular"]):
                        href = item.get("href")
                        if href:
                            full_url = href
                            if not full_url.startswith("http"):
                                full_url = f"{base_url}{full_url}"
                            
                            if text:
                                notices.append({
                                    "title": text,
                                    "url": full_url,
                                    "content": f"Notice from {name}: {text}",
                                    "source_name": name,
                                    "source_id": name.lower().replace(" ", "_"),
                                    "published_at": datetime.utcnow(),
                                    "country": "in"
                                })

            return notices[:10] # Limit to top 10 notices
        except requests.exceptions.RequestException as e:
            logger.error(f"Network error scraping {name} from {url}: {e}")
            return []
        except Exception as e:
            logger.error(f"Error scraping {name} from {url}: {e}")
            return []

    async def get_all_college_news(self) -> List[Dict[str, Any]]:
        sites = {
            "IIT Delhi": "https://home.iitd.ac.in/news.php", # Updated URL for IIT Delhi news
            "Mumbai University": "https://mu.ac.in/notices",
            "Anna University": "http://www.annauniv.edu/notices.php",
            "Delhi University": "https://www.du.ac.in/index.php?page=notifications"
        }
        all_news = []
        tasks = []
        for name, url in sites.items():
            tasks.append(self._scrape_site(name, url))
        
        results = await asyncio.gather(*tasks)
        for news_list in results:
            all_news.extend(news_list)
            
        return all_news

    def _save_articles(self, notices: List[Dict[str, Any]]) -> int:
        session = SessionLocal()
        count = 0
        try:
            for notice in notices:
                exists = session.query(RawNews).filter(RawNews.url == notice['url']).first()
                if not exists:
                    raw = RawNews(
                        source_id=notice['source_id'],
                        source_name=notice['source_name'],
                        title=notice['title'],
                        description=notice['content'],
                        url=notice['url'],
                        published_at=notice['published_at'],
                        content=notice['content'],
                        country=notice['country']
                    )
                    session.add(raw)
                    count += 1
            session.commit()
            return count
        except Exception as e:
            logger.error(f"Error saving student notices: {e}")
            session.rollback()
            return 0
        finally:
            session.close()

if __name__ == "__main__":
    scraper = CollegeScraper()
    scraper.run()
