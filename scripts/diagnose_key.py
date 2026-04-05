import json
import re
import base64

def check_key():
    with open('service-account.json', 'r') as f:
        data = json.load(f)
    
    pk = data['private_key']
    print(f"Key length: {len(pk)}")
    
    # Find the = byte
    for i, char in enumerate(pk):
        if char == '=':
            print(f"Found '=' at index {i} (Byte {i+1} approx)")

    # Extract clean base64
    clean = re.sub(r'-----BEGIN PRIVATE KEY-----|-----END PRIVATE KEY-----|\s', '', pk)
    print(f"Clean Base64 length: {len(clean)}")
    
    try:
        decoded = base64.b64decode(clean)
        print(f"✅ Successfully decoded Base64 (Binary length: {len(decoded)})")
    except Exception as e:
        print(f"❌ Base64 decode FAILED: {e}")

if __name__ == "__main__":
    check_key()
