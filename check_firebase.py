import json
import os
import base64

def check_service_account():
    path = "service-account.json"
    print(f"--- 📂 Deep Audit: {os.path.abspath(path)} ---")
    
    if not os.path.exists(path):
        print("❌ ERROR: service-account.json NOT FOUND!")
        return

    try:
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        print("✅ JSON is valid")
        
        pk = data.get('private_key', '')
        header = "-----BEGIN PRIVATE KEY-----"
        footer = "-----END PRIVATE KEY-----"
        
        if header not in pk or footer not in pk:
            print("❌ ERROR: PEM headers missing!")
            return

        # Extract core
        core = pk.split(header)[1].split(footer)[0]
        # Remove all whitespace
        core_clean = "".join(core.split())
        
        print(f"DEBUG: Core Base64 length = {len(core_clean)}")
        
        try:
            # Try to decode base64
            decoded = base64.b64decode(core_clean, validate=True)
            print("✅ Base64 content is VALID (decoded successfully)")
            print(f"DEBUG: Binary key length = {len(decoded)} bytes")
        except Exception as b64err:
            print(f"❌ ERROR: Base64 content is CORRUPT: {b64err}")
            print("💡 TIP: This usually means a character was accidentally deleted or changed during copy-paste.")

    except Exception as e:
        print(f"❌ ERROR reading file: {e}")

if __name__ == "__main__":
    check_service_account()
