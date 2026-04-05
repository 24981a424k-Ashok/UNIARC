import os
import sys
from loguru import logger
from dotenv import load_dotenv

# Load .env
load_dotenv()

# Ensure root is in path
sys.path.append(os.getcwd())

from src.config.firebase_config import initialize_firebase, verify_token

def debug_firebase():
    print("--- 🔍 Firebase Diagnostic Tool ---")
    
    try:
        # 1. Test Initialization
        app = initialize_firebase()
        if not app:
            print("❌ CRITICAL: Firebase failed to initialize with ANY method.")
            return
        
        print(f"✅ Firebase Initialized for Project: {app.project_id}")
    except Exception as e:
        import traceback
        print(f"❌ Diagnostic Crash: {e}")
        traceback.print_exc()
        return
    
    # 2. Check if we're using File or ENV
    if os.path.exists("service-account.json"):
        print("📁 Using [service-account.json] as primary source.")
    else:
        print("🌍 Using [Environment Variables] as primary source.")
    
    # 3. Basic Key Sanity
    pk = os.getenv("FIREBASE_PRIVATE_KEY")
    if pk:
        print(f"🔑 Private Key Found in ENV (Length: {len(pk)})")
        if "PRIVATE KEY" not in pk:
            print("⚠️  Warning: Private key in ENV might be missing PEM headers.")
    else:
        print("⚠️  Private Key NOT found in ENV.")

    print("\n🚀 Platform ready for authentication.")

if __name__ == "__main__":
    debug_firebase()
