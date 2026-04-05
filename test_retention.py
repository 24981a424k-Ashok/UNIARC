import requests

BASE_URL = "http://localhost:7860" # Based on main.py port
UID = "9CMrdFKvAMRdeEEN0atMmSlC10s1"

def test_status():
    try:
        url = f"{BASE_URL}/api/user/status?firebase_uid={UID}"
        print(f"Testing GET {url}")
        resp = requests.get(url)
        print(f"Status: {resp.status_code}")
        print(f"Body: {resp.json()}")
    except Exception as e:
        print(f"Request failed: {e}")

def test_ping():
    try:
        url = f"{BASE_URL}/api/user/ping_streak"
        print(f"Testing POST {url}")
        resp = requests.post(url, json={"firebase_uid": UID})
        print(f"Status: {resp.status_code}")
        print(f"Body: {resp.json()}")
    except Exception as e:
        print(f"Request failed: {e}")

if __name__ == "__main__":
    # Note: Requires the main.py server to be running (which it is, according to metadata)
    test_status()
    test_ping()
