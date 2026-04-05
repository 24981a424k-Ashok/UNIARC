import json
import os
import re

def setup_firebase():
    json_path = "service-account.json"
    env_path = ".env"
    
    if not os.path.exists(json_path):
        print(f"❌ Error: {json_path} not found in the current directory.")
        print("Please download your service account JSON from Firebase Console and save it as 'service-account.json'.")
        return

    try:
        with open(json_path, 'r') as f:
            data = json.load(f)
        
        print("✅ service-account.json loaded successfully.")
        
        # Sanitize Private Key for .env
        pk = data.get("private_key", "")
        # We want to store it in a way that our initialized_firebase logic can handle
        # Option A: Store the raw block with literal \n (standard)
        pk_env = pk.replace("\n", "\\n")
        
        updates = {
            "FIREBASE_PROJECT_ID": data.get("project_id"),
            "FIREBASE_PRIVATE_KEY_ID": data.get("private_key_id"),
            "FIREBASE_PRIVATE_KEY": pk_env,
            "FIREBASE_CLIENT_EMAIL": data.get("client_email"),
            "FIREBASE_CLIENT_ID": data.get("client_id"),
            "FIREBASE_CLIENT_CERT_URL": data.get("client_x509_cert_url")
        }
        
        # Read existing .env
        env_lines = []
        if os.path.exists(env_path):
            with open(env_path, 'r') as f:
                env_lines = f.readlines()
        
        # Update or Add keys
        new_lines = []
        keys_handled = set()
        for line in env_lines:
            match = re.match(r'^([^=]+)=(.*)$', line)
            if match:
                k, v = match.groups()
                if k in updates:
                    new_lines.append(f"{k}=\"{updates[k]}\"\n")
                    keys_handled.add(k)
                    continue
            new_lines.append(line)
            
        for k, v in updates.items():
            if k not in keys_handled:
                new_lines.append(f"{k}=\"{v}\"\n")
        
        with open(env_path, 'w') as f:
            f.writelines(new_lines)
            
        print(f"✅ {env_path} updated with Firebase credentials.")
        print("\n🚀 You can now restart your server.")
        
    except Exception as e:
        print(f"❌ Error during setup: {e}")

if __name__ == "__main__":
    setup_firebase()
