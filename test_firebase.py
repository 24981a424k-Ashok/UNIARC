import os
import sys
import json
from pathlib import Path
from dotenv import load_dotenv

# Add src to path
sys.path.append(str(Path(__file__).resolve().parent))

load_dotenv()

from src.config.firebase_config import initialize_firebase

if __name__ == "__main__":
    print("Full Debug - Testing Firebase Initialization...")
    
    path = "service-account.json"
    if os.path.exists(path):
        with open(path, 'r') as f:
            data = json.load(f)
            pk = data.get("private_key", "")
            print(f"Private Key Prefix: {pk[:50]}")
            print(f"Has literal \\n? {'\\n' in pk}")
            print(f"Has real newline? {'\n' in pk}")
            
            # If it has literal \n but no real fresh ones, maybe it needs fixing
            if "\\n" in pk and "\n" not in pk[30:-30]:
                print("FIXING literal \\n...")
                data["private_key"] = pk.replace("\\n", "\n")
                with open("service-account-fixed.json", "w") as fw:
                    json.dump(data, fw, indent=4)
                print("Created service-account-fixed.json")
    
    # Try initialization
    try:
        initialize_firebase()
        print("Success! Check logs.")
    except Exception as e:
        print(f"Initialization Failed: {e}")
