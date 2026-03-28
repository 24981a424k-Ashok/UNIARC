from src.database.models import SessionLocal, Newspaper, init_db
import logging

def seed_newspapers():
    db = SessionLocal()
    try:
        papers = [
            # India
            {"name": "Times of India", "url": "https://timesofindia.indiatimes.com", "country": "India", "logo_text": "TOI", "logo_color": "#000000"},
            {"name": "The Hindu", "url": "https://www.thehindu.com", "country": "India", "logo_text": "HINDU", "logo_color": "#000000"},
            {"name": "Indian Express", "url": "https://indianexpress.com", "country": "India", "logo_text": "IE", "logo_color": "#000000"},
            {"name": "Hindustan Times", "url": "https://www.hindustantimes.com", "country": "India", "logo_text": "HT", "logo_color": "#000000"},
            {"name": "Deccan Herald", "url": "https://www.deccanherald.com", "country": "India", "logo_text": "DH", "logo_color": "#022B58"},
            {"name": "The Print", "url": "https://theprint.in", "country": "India", "logo_text": "PRINT", "logo_color": "#e01a22"},
            {"name": "Livemint", "url": "https://www.livemint.com", "country": "India", "logo_text": "MINT", "logo_color": "#009040"},
            {"name": "Economic Times", "url": "https://economictimes.indiatimes.com", "country": "India", "logo_text": "ET", "logo_color": "#d91f27"},
            {"name": "NDTV", "url": "https://www.ndtv.com", "country": "India", "logo_text": "NDTV", "logo_color": "#e3000f"},
            {"name": "News18", "url": "https://www.news18.com", "country": "India", "logo_text": "N18", "logo_color": "#0055a4"},
            
            # USA
            {"name": "New York Times", "url": "https://www.nytimes.com", "country": "USA", "logo_text": "NYT", "logo_color": "#000000"},
            {"name": "Wall Street Journal", "url": "https://www.wsj.com", "country": "USA", "logo_text": "WSJ", "logo_color": "#010101"},
            {"name": "Washington Post", "url": "https://www.washingtonpost.com", "country": "USA", "logo_text": "WAPO", "logo_color": "#000000"},
            {"name": "CNN", "url": "https://www.cnn.com", "country": "USA", "logo_text": "CNN", "logo_color": "#cc0000"},
            {"name": "Fox News", "url": "https://www.foxnews.com", "country": "USA", "logo_text": "FOX", "logo_color": "#003366"},
            {"name": "USA Today", "url": "https://www.usatoday.com", "country": "USA", "logo_text": "USA", "logo_color": "#009BFF"},
            {"name": "NBC News", "url": "https://www.nbcnews.com", "country": "USA", "logo_text": "NBC", "logo_color": "#FFC000"},
            {"name": "Politico", "url": "https://www.politico.com", "country": "USA", "logo_text": "POL", "logo_color": "#cc0000"},
            
            # UK
            {"name": "The Guardian", "url": "https://www.theguardian.com", "country": "UK", "logo_text": "GUA", "logo_color": "#052962"},
            {"name": "BBC News", "url": "https://www.bbc.com/news", "country": "UK", "logo_text": "BBC", "logo_color": "#b91c1c"},
            {"name": "The Times", "url": "https://www.thetimes.co.uk", "country": "UK", "logo_text": "TIMES", "logo_color": "#000000"},
            {"name": "Financial Times", "url": "https://www.ft.com", "country": "UK", "logo_text": "FT", "logo_color": "#fcdcb5"},
            {"name": "The Telegraph", "url": "https://www.telegraph.co.uk", "country": "UK", "logo_text": "TELE", "logo_color": "#003366"},
            {"name": "The Independent", "url": "https://www.independent.co.uk", "country": "UK", "logo_text": "IND", "logo_color": "#e20000"},
            
            # Japan
            {"name": "The Japan Times", "url": "https://www.japantimes.co.jp", "country": "Japan", "logo_text": "JT", "logo_color": "#000000"},
            {"name": "Asahi Shimbun", "url": "https://www.asahi.com/ajw/", "country": "Japan", "logo_text": "ASAHI", "logo_color": "#ff0000"},
            {"name": "Nikkei Asia", "url": "https://asia.nikkei.com", "country": "Japan", "logo_text": "NIKK", "logo_color": "#004B87"},
            {"name": "Mainichi", "url": "https://mainichi.jp/english/", "country": "Japan", "logo_text": "MAIN", "logo_color": "#0055A4"},
            
            # Australia
            {"name": "Sydney Morning Herald", "url": "https://www.smh.com.au", "country": "Australia", "logo_text": "SMH", "logo_color": "#003b6e"},
            {"name": "The Australian", "url": "https://www.theaustralian.com.au", "country": "Australia", "logo_text": "AUST", "logo_color": "#000000"},
            {"name": "ABC News Aus", "url": "https://www.abc.net.au/news", "country": "Australia", "logo_text": "ABC", "logo_color": "#000000"},
            
            # France
            {"name": "Le Monde (En)", "url": "https://www.lemonde.fr/en/", "country": "France", "logo_text": "LMON", "logo_color": "#000000"},
            {"name": "France 24", "url": "https://www.france24.com/en/", "country": "France", "logo_text": "F24", "logo_color": "#00AEEF"},
            {"name": "Le Figaro", "url": "https://www.lefigaro.fr", "country": "France", "logo_text": "FIG", "logo_color": "#114f9d"},
            
            # Germany
            {"name": "DW News", "url": "https://www.dw.com/en/", "country": "Germany", "logo_text": "DW", "logo_color": "#005b9f"},
            {"name": "Der Spiegel", "url": "https://www.spiegel.de/international/", "country": "Germany", "logo_text": "SPG", "logo_color": "#e60000"},
            {"name": "Süddeutsche", "url": "https://www.sueddeutsche.de", "country": "Germany", "logo_text": "SZ", "logo_color": "#006437"},
            
            # Middle East
            {"name": "Al Jazeera", "url": "https://www.aljazeera.com", "country": "UAE", "logo_text": "AJZ", "logo_color": "#fa9c1d"},
            {"name": "Gulf News", "url": "https://gulfnews.com", "country": "UAE", "logo_text": "GULF", "logo_color": "#0047b3"},
            {"name": "Khaleej Times", "url": "https://www.khaleejtimes.com", "country": "UAE", "logo_text": "KHLJ", "logo_color": "#1a1a1a"},
            
            # Singapore / China / Asia
            {"name": "South China Post", "url": "https://www.scmp.com", "country": "China", "logo_text": "SCMP", "logo_color": "#003366"},
            {"name": "Straits Times", "url": "https://www.straitstimes.com", "country": "Singapore", "logo_text": "ST", "logo_color": "#cc0000"},
            {"name": "CNA", "url": "https://www.channelnewsasia.com", "country": "Singapore", "logo_text": "CNA", "logo_color": "#e60000"},
            {"name": "Xinhua (En)", "url": "https://english.news.cn/", "country": "China", "logo_text": "XIN", "logo_color": "#cf0a2c"},
            
            # Russia
            {"name": "RT", "url": "https://www.rt.com", "country": "Russia", "logo_text": "RT", "logo_color": "#8fB837"},
            {"name": "TASS", "url": "https://tass.com", "country": "Russia", "logo_text": "TASS", "logo_color": "#1c3d79"},
            {"name": "Moscow Times", "url": "https://www.themoscowtimes.com", "country": "Russia", "logo_text": "MT", "logo_color": "#cc0000"},
            
            # Global
            {"name": "Reuters", "url": "https://www.reuters.com", "country": "Global", "logo_text": "REU", "logo_color": "#ff8000"},
            {"name": "Bloomberg", "url": "https://www.bloomberg.com", "country": "Global", "logo_text": "BLM", "logo_color": "#000000"},
            {"name": "AP News", "url": "https://apnews.com", "country": "Global", "logo_text": "AP", "logo_color": "#E31837"}
        ]

        added_count = 0
        existing_names = [n.name for n in db.query(Newspaper).all()]

        for p in papers:
            if p["name"] not in existing_names:
                paper = Newspaper(**p)
                db.add(paper)
                added_count += 1
        
        db.commit()
        print(f"Successfully seeded {added_count} new newspapers.")
    except Exception as e:
        db.rollback()
        print(f"Error seeding newspapers: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    init_db()
    seed_newspapers()
