import requests
import json

BASE_URL = "http://127.0.0.1:8000" # Match user's restored port

def test_endpoint(name, method, path, payload=None, params=None):
    url = f"{BASE_URL}{path}"
    try:
        if method == "GET":
            resp = requests.get(url, params=params)
        else:
            resp = requests.post(url, json=payload)
        
        if resp.status_code == 200:
            print(f"✅ {name}: SUCCESS (200)")
            return resp.json()
        elif resp.status_code == 404:
             print(f"❌ {name}: FAILED (404 Not Found) - Check routing.")
        else:
            print(f"⚠️ {name}: UNEXPECTED ({resp.status_code}) - {resp.text[:100]}")
    except Exception as e:
        print(f"❌ {name}: CONNECTION ERROR - {e}")
    return None

def run_tests():
    print(f"Checking connections on {BASE_URL}...")
    
    # 1. Health Check
    test_endpoint("Home Page", "GET", "/")
    
    # 2. User Status (Uses existing user or creates mock)
    test_endpoint("User Status API", "GET", "/api/user/status", params={"uid": "test_ai_agent_uid"})
    
    # 3. Translation API (Batch)
    stories = [{"title": "AI News is great", "bullets": ["First point", "Second point"]}]
    test_endpoint("Translation API", "POST", "/api/translate-node", payload={"stories": stories, "lang": "Hindi"})
    
    # 4. Streak Ping
    test_endpoint("Streak Ping API", "POST", "/api/user/ping_streak", payload={"firebase_uid": "test_ai_agent_uid"})

if __name__ == "__main__":
    run_tests()
