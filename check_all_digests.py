from src.database.models import SessionLocal, DailyDigest

def check():
    db = SessionLocal()
    try:
        all_digests = db.query(DailyDigest).order_by(DailyDigest.date.desc()).all()
        print(f"Total Digests: {len(all_digests)}")
        for d in all_digests[:5]:
            print(f"ID: {d.id}, Date: {d.date}, Published: {d.is_published}")
    finally:
        db.close()

if __name__ == "__main__":
    check()
