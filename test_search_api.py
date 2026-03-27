import requests

def test_search():
    url = "http://127.0.0.1:8000/api/search-news"
    params = {
        "interests": "Defense & Security",
        "page": 1
    }
    try:
        resp = requests.get(url, params=params)
        print(f"Status: {resp.status_code}")
        data = resp.json()
        print(f"Count: {len(data.get('articles', []))}")
        if data.get('articles'):
            print("First article:", data['articles'][0]['title'])
        else:
            print("No articles found.")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_search()
