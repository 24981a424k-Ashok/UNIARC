import os
import sys

def check_env():
    print("="*40)
    print("ENVIRONMENT CONFIGURATION CHECK")
    print("="*40)

    required_vars = [
        "OPENAI_API_KEY",
        "NEWS_API_KEY",
        "DATABASE_URL"
    ]
    
    optional_vars = [
        "FIREBASE_API_KEY",
        "FIREBASE_SERVICE_ACCOUNT_JSON",
        "VAPID_PUBLIC_KEY",
        "VAPID_PRIVATE_KEY"
    ]

    all_good = True

    print("\n[ CRITICAL VARIABLES ]")
    for var in required_vars:
        value = os.getenv(var)
        if value:
            # Mask key for security
            masked = value[:4] + "*" * (len(value)-4) if len(value) > 4 else "****"
            print(f"✅ {var}: Found ({masked})")
        else:
            print(f"❌ {var}: MISSING")
            all_good = False

    print("\n[ OPTIONAL / DEPLOYMENT VARIABLES ]")
    for var in optional_vars:
        value = os.getenv(var)
        if value:
             print(f"✅ {var}: Found")
        else:
             print(f"⚠️  {var}: Not set")

    print("\n" + "="*40)
    if all_good:
        print("✅ Environment looks good for basic operation.")
    else:
        print("❌ Critical variables are missing. Please check .env or Space secrets.")
    
    # Check for .env file
    if os.path.exists(".env"):
        print("\n✅ .env file found.")
    else:
        print("\n⚠️  No .env file found (Normal for Cloud/Space deployment if secrets are set).")

if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()
    check_env()
