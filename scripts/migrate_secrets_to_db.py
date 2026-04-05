import os
from dotenv import load_dotenv
from src.database.models import init_db
from src.utils.secret_manager import SecretManager

def migrate():
    # 1. Load current environment (from .env)
    load_dotenv()
    
    # 2. Ensure DB tables exist
    print("Initializng database schema...")
    init_db()
    
    # 3. List of keys to migrate
    keys_to_migrate = [
        "NEWS_API_KEY",
        "GNEWS_API_KEY",
        "GNEWS_API_KEY_2",
        "OPENAI_API_KEY",
        "NEWSDATA_API_KEY",
        "CRICKET_API_KEY",
        "GROQ_API_KEY",
        "GROQ_API_KEY_1",
        "GROQ_API_KEY_2",
        "GROQ_API_KEY_3",
        "GROQ_KEY_TELUGU",
        "GROQ_KEY_HINDI",
        "GROQ_KEY_MALAYALAM",
        "GROQ_KEY_TAMIL",
        "GROQ_KEY_CRYSTAL_BALL",
        "TRANSLATION_OPENAI_KEY_1",
        "TRANSLATION_OPENAI_KEY_2",
        "TRANSLATION_OPENAI_KEY_3",
        "FIREBASE_API_KEY",
        "FIREBASE_AUTH_DOMAIN",
        "FIREBASE_PROJECT_ID",
        "FIREBASE_STORAGE_BUCKET",
        "FIREBASE_MESSAGING_SENDER_ID",
        "FIREBASE_APP_ID",
        "VAPID_PUBLIC_KEY",
        "VAPID_PRIVATE_KEY",
        "TWILIO_ACCOUNT_SID",
        "TWILIO_AUTH_TOKEN",
        "TWILIO_PHONE_NUMBER"
    ]
    
    print(f"Starting migration of {len(keys_to_migrate)} keys to PostgreSQL...")
    
    migrated_count = 0
    skipped_count = 0
    
    for key in keys_to_migrate:
        value = os.getenv(key)
        if value:
            # Check if it's already there (don't overwrite unless we want to)
            # SecretManager.set already handles update vs insert
            SecretManager.set(key, value, description=f"Migrated from .env on startup")
            migrated_count += 1
        else:
            skipped_count += 1
            
    print(f"\nMigration Complete!")
    print(f"✅ Keys Migrated/Updated: {migrated_count}")
    print(f"ℹ️  Keys Missing in .env: {skipped_count}")
    print("\nYou can now safely remove these keys from your Hugging Face Environment Variables (except DATABASE_URL).")

if __name__ == "__main__":
    migrate()
