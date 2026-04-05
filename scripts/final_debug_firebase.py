import os
import json
import re
import traceback
from dotenv import load_dotenv
import firebase_admin
from firebase_admin import credentials

def final_debug():
    load_dotenv()
    json_str = os.getenv("FIREBASE_SERVICE_ACCOUNT_JSON")
    print(f"JSON Found: {bool(json_str)}")
    
    try:
        config = json.loads(json_str)
        pk = str(config["private_key"])
        print(f"Raw PK start: {pk[:30]}")
        
        pk_clean = re.sub(r'-----BEGIN PRIVATE KEY-----|-----END PRIVATE KEY-----|[\s\\n]', '', pk)
        chunks = [pk_clean[i:i+64] for i in range(0, len(pk_clean), 64)]
        pk_wrapped = "\n".join(chunks)
        config["private_key"] = f"-----BEGIN PRIVATE KEY-----\n{pk_wrapped}\n-----END PRIVATE KEY-----\n"
        
        print("Attempting Cert initialization...")
        cred = credentials.Certificate(config)
        app = firebase_admin.initialize_app(cred, name="debug_app")
        print(f"✅ SUCCESS! Initialized Project: {app.project_id}")
        
    except Exception as e:
        print(f"❌ FAILED: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    final_debug()
