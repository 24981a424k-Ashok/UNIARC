from datetime import datetime
from src.database.models import SessionLocal, RawNews, VerifiedNews, DailyDigest

def seed_data():
    session = SessionLocal()
    
    # Check if we have data
    if session.query(DailyDigest).count() > 0:
        print("Data already exists. Skipping seed.")
        return

    print("Seeding dummy data...")
    
    # Create Dummy Daily Digest
    digest_data = {
        "date": datetime.utcnow().strftime("%Y-%m-%d"),
        "insight": "AI is transforming news intelligence by automating collection and analysis.",
        "top_stories": [
            {
                "title": "AI Agent Successfully Deployed",
                "bullets": ["Agent built in record time", "Uses LLMs for analysis", "Runs automatically every 24h"],
                "why": "Demonstrates the power of autonomous coding agents."
            },
            {
                "title": "Global Tech Markets Rally",
                "bullets": ["Nasdaq up 2%", "AI stocks leading the charge", "Investors optimistic about 2026"],
                "why": "Economic stability impacts global trade."
            }
        ],
        "categories": {
            "Technology": [
                {"title": "New Quantum Chip Released", "why": "Major breakthrough in computing speed."}
            ],
            "Business": [
                {"title": "Startup raises $100M for Clean Energy", "why": "Shift towards sustainable power."}
            ]
        },
        "generated_at": datetime.utcnow().isoformat()
    }
    
    digest = DailyDigest(
        content_json=digest_data,
        is_published=True
    )
    session.add(digest)
    
    session.commit()
    print("Seed data added.")
    session.close()

if __name__ == "__main__":
    seed_data()
