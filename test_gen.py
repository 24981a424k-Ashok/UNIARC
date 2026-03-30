import asyncio
import os
import sys
from sqlalchemy.orm import Session

# Ensure src is in path
sys.path.append(os.getcwd())

from src.database.models import SessionLocal
from src.digest.generator import DigestGenerator

async def test_digest():
    db = SessionLocal()
    try:
        print("Starting direct digest generation...")
        generator = DigestGenerator()
        digest = await generator.create_daily_digest(db)
        print("Success! Digest generated.")
        
        # Verify China/UAE in the returned digest
        countries = digest.get("countries", {})
        print(f"Total keys in countries map: {len(countries)}")
        for name in sorted(countries.keys()):
            # Use ASCII-safe printing
            print(f"- {name}: {len(countries[name])} stories")
            
    except Exception as e:
        print(f"FAILED: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    asyncio.run(test_digest())
