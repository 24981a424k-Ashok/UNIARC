from src.database.models import SessionLocal, Newspaper, init_db
import logging

def seed_newspapers():
    db = SessionLocal()
    try:
        # Check if already seeded
        if db.query(Newspaper).count() > 0:
            print("Newspapers already seeded.")
            return

        papers = [
            # India
            {"name": "Times of India", "url": "https://timesofindia.indiatimes.com", "country": "India", "logo_text": "TOI", "logo_color": "#000000"},
            {"name": "The Hindu", "url": "https://www.thehindu.com", "country": "India", "logo_text": "HINDU", "logo_color": "#000000"},
            {"name": "Indian Express", "url": "https://indianexpress.com", "country": "India", "logo_text": "IE", "logo_color": "#000000"},
            {"name": "Hindustan Times", "url": "https://www.hindustantimes.com", "country": "India", "logo_text": "HT", "logo_color": "#000000"},
            
            # USA
            {"name": "New York Times", "url": "https://www.nytimes.com", "country": "USA", "logo_text": "NYT", "logo_color": "#000000"},
            {"name": "Wall Street Journal", "url": "https://www.wsj.com", "country": "USA", "logo_text": "WSJ", "logo_color": "#010101"},
            {"name": "Washington Post", "url": "https://www.washingtonpost.com", "country": "USA", "logo_text": "WAPO", "logo_color": "#000000"},
            {"name": "CNN", "url": "https://www.cnn.com", "country": "USA", "logo_text": "CNN", "logo_color": "#cc0000"},
            
            # UK
            {"name": "The Guardian", "url": "https://www.theguardian.com", "country": "UK", "logo_text": "GUA", "logo_color": "#052962"},
            {"name": "BBC News", "url": "https://www.bbc.com/news", "country": "UK", "logo_text": "BBC", "logo_color": "#b91c1c"},
            {"name": "The Times", "url": "https://www.thetimes.co.uk", "country": "UK", "logo_text": "TIMES", "logo_color": "#000000"},
            
            # Japan
            {"name": "The Japan Times", "url": "https://www.japantimes.co.jp", "country": "Japan", "logo_text": "JT", "logo_color": "#000000"},
            {"name": "Asahi Shimbun", "url": "https://www.asahi.com/ajw/", "country": "Japan", "logo_text": "ASAHI", "logo_color": "#ff0000"},
            
            # Global
            {"name": "Reuters", "url": "https://www.reuters.com", "country": "Global", "logo_text": "REU", "logo_color": "#ff8000"},
            {"name": "Bloomberg", "url": "https://www.bloomberg.com", "country": "Global", "logo_text": "BLM", "logo_color": "#000000"},
            {"name": "Al Jazeera", "url": "https://www.aljazeera.com", "country": "Global", "logo_text": "AJZ", "logo_color": "#fa9c1d"}
        ]

        for p in papers:
            paper = Newspaper(**p)
            db.add(paper)
        
        db.commit()
        print(f"Successfully seeded {len(papers)} newspapers.")
    except Exception as e:
        db.rollback()
        print(f"Error seeding newspapers: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    init_db()
    seed_newspapers()
